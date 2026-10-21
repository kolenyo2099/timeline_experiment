# Flight reconciliation (2026-10-21)

The question was why the timeline's flight ledgers have 141 rows and `transfers.csv` has 111. The answer: there are 114 flights, and the tally drives all three sources.

| Source | Rows | What it is |
|---|---|---|
| Tally `Spreadsheet_For_Michael.xlsx` › Database_map | **102** | flights itemised by the tally: the source of truth |
| `contact-layer/transfers.csv` (= `sorting-room/removals.csv`) | 111 | the tally's 102, plus 9 rows for countries the tally does not itemise |
| `graph.html` "Recorded transfers" ledgers | 141 | the 114 unique flights, with 27 rows counted twice |

`sync_flight_ledgers.py --dry-run` already rebuilds the CSV and the ledgers from the tally. It makes no change to the counts, so nothing was out of sync with the tally.

## Where 141 comes from

- **Costa Rica 21 + Paraguay 6 = 27 rows listed twice.** Each country's ledger sits on two agreement events: `ag-7` and `ag-8`, and `ag-25` and `ag-26`. These are the same flights, not extra ones.
- **9 rows outside the tally**, kept from hand research because the tally does not itemise these countries: Guatemala 1, Kosovo 1, Kuwait 2, Poland 4, Qatar 1. The CSV has them too.
- **3 rows only in the graph**, also hand research:
  - Poland 2026-04-30, Russians
  - Israel 2026-06-09, Palestinians
  - Israel 2026-06-09, Russians and other nationalities

  The sync script keeps these on purpose ("no headcount to double, but real content").

102 + 9 + 3 = **114 flights**, and 141 − 27 = 114.

## What the flights layer plots

One mark per unique (country, date, row) taken from the graph ledgers: **114 flights**. Rows dated "Date not recorded" stay in their country's panel and never go on the time axis.

The tally stays the source of truth: change it, then run `uv run sync_flight_ledgers.py`, and the layer follows.

Open item: the 3 graph-only rows have no tally or CSV row. They should be added to the tally, or marked as hand research.
