"""Build the timeline experiment: index.html's record, and layers.js beside it.

  record     index.html is a fork of removals-timeline/graph.html. Its DATA block
             is copied over from graph.html on every build, so the record and its
             flight ledgers (driven from the tally by sync_flight_ledgers.py)
             never drift; everything else in index.html is the experiment's own.
  meetings   the meetings explorer (USAspending ai test/meetings): every meeting
             with a timeline country, its document leads, and the hand-verified
             meetings in contact-layer/research, which outrank it
  operators  flight operator by country and date, from contact-layer/transfers.csv

Every meeting carries a provenance tier, shown on the page as-is:
  verified   matches a row in contact-layer/research/verified_*.csv
  sourced    machine-extracted, at least one source supports it, and it occurred
  inferred   machine-extracted, and planned, unclear or with a vague counterpart

  python3 build_layers.py          # writes layers.js; keeps the old one if the
                                   # meetings folder is not on this machine
"""
import csv, json, os, re, sys
from pathlib import Path

HERE = Path(__file__).parent
APPS = HERE.parent
MEETINGS = Path(os.environ.get("MEETINGS_DIR",
                               Path.home() / "Documents/USAspending ai test/meetings"))
OUT = HERE / "layers.js"
FIRST, LAST = "2025-01-20", "2026-09-30"     # the timeline's own span, plus a month
ALIAS = {"DRC": "Democratic Republic of the Congo", "DR Congo": "Democratic Republic of the Congo",
         "St Kitts and Nevis": "Saint Kitts and Nevis", "St Kitts & Nevis": "Saint Kitts and Nevis",
         "Swaziland": "Eswatini", "Cape Verde": "Cabo Verde"}
QUOTE = 300                                  # evidence is cut to this many characters


PAGE = HERE / "index.html"
RECORD = APPS / "removals-timeline/graph.html"
DATA_BLOCK = re.compile(r'<script id="tcr-data">.*?</script>', re.S)


def sync_record():
    """Copy the record's DATA block from graph.html into index.html."""
    block = DATA_BLOCK.search(RECORD.read_text(encoding="utf-8")).group(0)
    page = PAGE.read_text(encoding="utf-8")
    assert len(DATA_BLOCK.findall(page)) == 1, "index.html must hold exactly one DATA block"
    PAGE.write_text(DATA_BLOCK.sub(lambda _: block, page), encoding="utf-8")


def members():
    """The countries the page draws, read from its LINES, so the two cannot drift."""
    html = PAGE.read_text(encoding="utf-8")
    return {c for block in re.findall(r"members: \[([^\]]*)\]", html)
            for c in re.findall(r'"([^"]+)"', block)}


def surname(name):
    return re.sub(r"[^a-z]", "", name.split()[-1].lower()) if name.strip() else ""


def rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build():
    scope = members()
    meet = rows(MEETINGS / "meetings.csv")
    leads = rows(MEETINGS / "official_document_leads.csv")
    officials = {surname(r["name"]): r["name"] for r in rows(MEETINGS / "officials.csv")}

    leads_of = {}
    for L in leads:
        i = int(L["meeting_csv_row"]) - 2          # a file line number: header is line 1
        m = meet[i]
        assert (m["official"], m["date"]) == (L["official"], L["meeting_date"]), L["meeting_csv_row"]
        leads_of.setdefault(i, []).append({
            "cat": L["document_category"].replace("_", " "),
            "ref": L["document_reference"].strip()[:160],
            "sent": L["mention_sentence"].strip()[:QUOTE],
            "url": L["source_url"], "title": L["source_title"][:140]})

    verified = {}
    for f in sorted((APPS / "contact-layer/research").glob("verified_*.csv")):
        for r in rows(f):
            c = ALIAS.get(r["country"].strip(), r["country"].strip())
            if c in scope and FIRST <= r["date"] <= LAST:
                verified[(r["date"], c, surname(r["us_official"]))] = r

    out, seen = [], {}
    for i, m in enumerate(meet):
        countries = [ALIAS.get(c.strip(), c.strip()) for c in m["countries"].split(";")]
        mine = [c for c in countries if c in scope]
        if not mine or m["status"] == "cancelled" or "us_only" in m["flags"]:
            continue
        if m["date"] and not FIRST <= m["date"] <= LAST:
            continue
        vague = "vague_counterpart" in m["flags"] or "unnamed_counterpart" in m["flags"]
        if vague and not m["date"]:                # no date and no one named: nothing to go on
            continue
        tier = ("sourced" if m["status"] == "occurred" and int(m["n_supported"] or 0) >= 1
                and not vague else "inferred")
        for c in mine:
            key = (m["date"], c, surname(m["official"]))
            if m["date"] and key in seen:          # same meeting, another extraction
                prev = seen[key]
                prev["src"] = sorted(set(prev["src"]) | set(m["sources"].split()))[:4]
                prev["leads"] += leads_of.get(i, [])
                continue
            v = verified.pop(key, None) if m["date"] else None
            rec = {"date": m["date"], "country": c, "official": m["official"],
                   "cp": m["counterparts"], "type": m["type"], "status": m["status"],
                   "place": m["place"], "occasion": m["occasion"][:200],
                   "tier": "verified" if v else tier,
                   "src": m["sources"].split()[:3] + ([v["source_url"]] if v else []),
                   "ev": m["evidence"][:QUOTE], "leads": leads_of.get(i, [])}
            seen[key] = rec
            out.append(rec)

    # Verified meetings the explorer never found are meetings all the same.
    for (date, c, sur), v in verified.items():
        out.append({"date": date, "country": c, "official": officials.get(sur, v["us_official"]),
                    "cp": f'{v["foreign_official"]} [{v["foreign_role"]}] ({c})',
                    "type": "in_person", "status": "occurred", "place": "", "occasion": "",
                    "tier": "verified", "src": [v["source_url"]],
                    "ev": v["evidence_summary"][:QUOTE], "leads": []})

    out.sort(key=lambda r: (r["date"] or "9999", r["country"], r["official"]))
    for n, r in enumerate(out):
        r["id"] = f"mt-{n}"

    operators = {}
    for r in rows(APPS / "contact-layer/transfers.csv"):
        c = ALIAS.get(r["country"].strip(), r["country"].strip())
        if r["date"] and r["contractor"].strip():
            operators[f'{c}|{r["date"]}'] = r["contractor"].strip()
    return out, operators


def check(meetings):
    """The smallest thing that fails if the join or the tiers break."""
    assert meetings, "no meetings in scope"
    assert {m["tier"] for m in meetings} <= {"verified", "sourced", "inferred"}
    assert all(m["status"] != "cancelled" for m in meetings)
    dated = [(m["date"], m["country"], surname(m["official"])) for m in meetings if m["date"]]
    assert len(dated) == len(set(dated)), "duplicate meeting after dedupe"


if __name__ == "__main__":
    sync_record()
    print(f"  index.html: record copied from {RECORD.relative_to(APPS)}")
    if not (MEETINGS / "meetings.csv").exists():
        print(f"  meetings folder not found at {MEETINGS}; layers.js left as it is")
        sys.exit(0)
    meetings, operators = build()
    check(meetings)
    tiers = {t: sum(m["tier"] == t for m in meetings) for t in ("verified", "sourced", "inferred")}
    OUT.write_text("/* Generated by build_layers.py -- do not edit. Machine-extracted layers,\n"
                   "   not reviewed unless tier is \"verified\". */\n"
                   "window.TCR_LAYERS = " + json.dumps(
                       {"meetings": meetings, "operators": operators},
                       ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"  {len(meetings)} meetings ({sum(1 for m in meetings if m['date'])} dated; {tiers}), "
          f"{sum(len(m['leads']) for m in meetings)} document leads, {len(operators)} flight operators "
          f"-> {OUT.name} ({OUT.stat().st_size // 1024} KB)")
