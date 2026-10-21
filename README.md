# Timeline experiment

A fork of the HRC removals timeline that adds every recorded flight and the diplomatic meetings around the deals. Open `index.html`.

- The record (agreements, restrictions, flight ledgers) is copied from `removals-timeline/graph.html` in the main project on every build. Fix facts there.
- The meetings and the document leads in `layers.js` are machine-extracted and **unreviewed** unless marked "HRC-verified". `build_layers.py` builds them from the meetings explorer and the contact-layer research.
- Rebuild from the main project with `./build_all.sh`, or run `python3 build_layers.py` here.

See `PROPOSAL_v2.md` for the design and the next phases (FOIA tray, actor matrix, press layer), and `flight_reconciliation.md` for why the flight count is 114, not 141.
