# Removals timeline v2 — flights, meetings, press, FOIA

Status: proposal, nothing built. Drafted 2026-10-21. A Sonnet draft was reviewed and changed; the changes are marked **[changed]**.

## What we have (from the exploration)

| Source | What it holds | Trust |
|---|---|---|
| Timeline `graph.html` DATA | 172 events, hand-edited | fact-checked |
| Flight ledgers / `transfers.csv` | 141 ledger rows vs 111 CSV rows, **not reconciled**; only 5 flights plotted today | reviewed, but inconsistent |
| Meetings explorer `meetings.csv` | 4,017 meetings by 28 US officials; **441 in scope countries + window, 456 in scope but undated** | LLM-extracted, unreviewed |
| `official_document_leads.csv` | 1,489 document leads; **354 in scope countries** | LLM-extracted, "mentioned", not proven to exist |
| contact-layer meeting files | press events, State schedule, 25 hand-verified meetings | mixed; overlaps the meetings above |
| Research pipeline | 1,837 articles, Mar–Sep 2026; 10.7k entities, 9.6k relations, no IDs, no event dates | LLM-extracted, ~18% syndicated duplicates |

## 1. One public timeline, every layer, provenance visible

Decision (2026-10-21): every layer goes on the public timeline (flights, meetings, leads, press, actors, FOIA tray). The unreviewed layers are off by default and hatched.

A hatch pattern alone gets lost in a screenshot, a quote or an export, so the label travels in words too:
- Every unreviewed item carries the text **"Unreviewed · machine-extracted"** in its tooltip, its dossier row and its CSV or draft export, as well as the hatch.
- Turning on an unreviewed chip shows a one-line notice above the canvas while that chip is on: "Meetings are machine-extracted from public sources and not yet reviewed by HRC."
- Headline counts are split into reviewed and unreviewed ("Meetings 441, unreviewed"), never one merged total.
- Planned and unclear meetings say so in words, not just with a dashed outline.

Size: the record and flights stay inline, so the page still opens offline. The other layers load as JSON files beside `graph.html` the first time their chip is turned on.

A row becomes verified (solid) only when someone reviews it (v3 reviewer mode, or by hand into the registry).

## 2. The canvas

The default stays the current story: six regional lines, four "Arrangements" chips on.

| Layer | Zoomed out | Drilled to a region or country |
|---|---|---|
| Flights (reviewed, off by default) | One small tick per flight under the country lane, height = people on board | Hover: date, count, nationalities, layovers, operator or "unidentified operator". Never a tail number. |
| Meetings (unreviewed, hatched) | **Monthly** heat strip per lane, aligned with the flight ticks **[changed: monthly, not 2-month]** | One tick per meeting. Fill = type, outline = status (planned dashed, unclear hollow). |
| Document leads (unreviewed, hatched) | No marks; a count badge on the meeting or station | Listed in the dossier and the tray |
| Press (unreviewed, hatched) | A separate thin strip, labelled **"published"**, never in the event band | Headlines, one per syndication cluster |

Undated meetings (456) never go on the axis. More than ~150 marks in view falls back to the strip, with a line saying why.

## 3. The country dossier replaces tabbed panels **[changed]**

The draft split a country's panel into Record / Flights / Meetings / Leads / Press tabs. Tabs hide what an investigator is looking for: the **sequence** (Boulos visits, two weeks later an MOU, a month later the first flight). The panel becomes one merged chronology:

```
2025-06-03  ● MEETING   Landau – FM X, Washington   [unreviewed · 2 sources]   2 leads
2025-06-18  ◆ RECORD    MOU signed                  [verified]
2025-07-11  ▲ FLIGHT    14 people · Venezuela, Cuba · unidentified operator
            ...
Undated (12) ▸
```

It has kind chips to filter, a provenance badge on every row, and actor chips that open the actor card. This answers "who negotiated what, and what followed" for one country, and it is the main working screen for an investigator.

## 4. Actors

- `actors.csv`: `actor_id, name, type, aliases, country_id, reviewed`. Seeds: the 28 officials; the companies GEO Group, CoreCivic, GlobalX, CSI Aviation, Acquisition Logistics, MTC, Eastern Air Express, Omni, Journey Air, Amentum, Palantir, Akima, GardaWorld and Loyal Source; and the top ~300 press entities merged by hand. Countries use the registry's IDs.
- Linking is by exact alias match only. Unmatched strings stay unlinked.
- **Actors view** (`#/actors`) is one matrix component with a switchable row type **[changed]**:
  - US official × country: cells are meeting counts. This shows who negotiates where.
  - Company × country: cells are flights operated, plus press and contract mentions. This surfaces the companies.

  Clicking a cell opens the matching rows in the dossier. There is no network graph; the research pipeline already has one.
- Rule: a company is linked to a flight only from a sourced `contractor` field. A company named in a press article never fills in a flight's operator.

## 5. FOIA tray: request the records behind the event, not the event **[changed]**

The draft turned each lead into a request row. Two problems:
- Readouts are already public.
- Investigators file one request per agency component covering many events, not one per lead.

The tray works like this instead.

**Event type → the records worth asking for:**

| Event | Records to request | Where |
|---|---|---|
| Meeting | memorandum of conversation (memcon), briefing memo / scene-setter cable, delegation list, trip itinerary, talking points | State: the official's bureau (WHA, AF, PRM, Office of the Deputy Secretary) |
| Agreement or MOU | drafts and annexes, operating procedures, diplomatic notes, Circular 175 authorization | State L / bureau; DHS PLCY |
| Flight | ICE Air manifests (passengers redacted), charter task order, country-clearance cables, airport and operator notices | ICE ERO / ICE Air; State (clearances) |
| Payment or contract | award, modifications, invoices | **check USAspending/FPDS first** (the meetings folder already has USAspending tooling), then FOIA what isn't there |

- A lead from `official_document_leads` or the press (Jamaica draft MOU, Liberia MOU, Antigua per-head proposal, the Love Field emails, the AP-reported State memo) becomes a named record inside a request. It never stands as its own request.
- **Batching:** the tray groups rows by agency and component and merges the date ranges, so it produces one draft request per component. Each draft lists the officials, counterparts, date range and named records, and every claim carries its evidence quote and URL.
- Agency and office come from a small hand-kept `official_offices.csv` (official → agency, bureau, tenure). It is suggested, and the investigator confirms it.
- **Status per request:** drafted, filed, tracking number, due date, response. Without this the tray only produces drafts; with it, it becomes the FOIA log. Each lead also carries a flag: *mentioned* or *confirmed to exist*.
- Export: CSV of requests plus one Markdown draft per agency.

## 6. Scope **[changed]**

- **Meetings:** keep all **441** dated meetings in scope countries and in the window, and drop the 7 cancelled. The draft's "is one of the 28 officials" test filters nothing, because the file is built from those 28. A topic keyword filter would hide context: a security meeting with El Salvador is part of the negotiation. Topic hits become a **highlight**, not a filter. Exclusions go in `meetings_scope_overrides.csv`.
- **Dedupe:** across `meetings.csv` and the contact-layer meeting files, on date + official + country, keeping the row with the highest provenance. The others become extra sources.
- **Leads:** the 354 in-scope leads, linked to their meeting.
- **Press:** one article per syndication cluster, kept only if it names a scope country and (a seeded company or a scope keyword).
- **Project rules carried over:**
  - Countries come from the registry, including the with-Ghana and without-Ghana variants.
  - **Money figures from the press are never shown as figures.** Funding comes only from whopays, so a press amount appears only as a FOIA lead.
  - Aircraft are redacted.
  - An unsourced operator reads "unidentified operator".

## 7. Data model (v1, kept small) **[changed]**

The draft proposed five tables plus a link table. v1 needs three generated JSON files and no link table:

- `events`: kind (flight / meeting / article), date, date_precision, country_id, title, status, provenance, `actor_ids` (|-list), `source_urls`.
- `actors`.
- `requests` / `leads`.

A `build_layers.py` builds them from the source CSVs, the same way `sync_flight_ledgers.py` does today; nothing is hand-edited. A link table comes later, if actor-to-actor roles become necessary.

Provenance has three tiers, drawn the same way everywhere:
- **verified** (solid)
- **sourced, unreviewed** (hatched)
- **inferred** (hollow)

Status (planned, unclear) is a separate outline.

## 8. Phasing

**v1** (built 2026-10-21: 111 dated flights, 516 dated + 131 undated meetings, 573 document leads; `build_layers.py` → `layers.js`, run by `build_all.sh`)
1. Reconcile the flights: 141 ledger rows vs 111 CSV rows against the tally, written up in `flight_reconciliation.md`. This blocks everything else.
2. A flights chip with every flight plotted.
3. Meetings as monthly hatched cells (a cell opens that month's list, instead of one tick per meeting), the country dossier, provenance hatching and labels, and actor chips for 28 officials and about 15 companies.
4. Build, then publish to the removals-timeline remote.

**v2**
- FOIA tray: event → records, batching by agency, status log, export.
- Actors matrix: official × country and company × country.

**v3**
- Press layer.
- Reviewer mode that promotes rows to verified.
- Event extraction from articles.

## 9. Before building: decisions and risks

1. ~~Two editions?~~ Decided: one public page, every layer, unreviewed layers hatched and labelled.
2. **Flights source of truth:** the tally ledger (141) or `transfers.csv` (111)?
3. **Who reviews** the 441 meetings and the leads, so they move from hatched to verified?
6. **Named foreign counterparts** go public in the meetings layer. Should unnamed or low-level staff ("[Technical team]") stay as roles only?
4. **Secrets:** `apps/contact-layer/serper.txt` is untracked in this repo. It must be gitignored before any commit, and the meetings pipeline keeps keys in plaintext files.
5. **Press dates** are publication dates and cover only Mar–Sep 2026, so earlier months look quiet. The UI says so.
