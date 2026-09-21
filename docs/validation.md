# Validation status

## Evidence levels

- **Original integration:** real report edits through Codex on native Windows with Chrome and Playwright Extension. Source reconnection, chart fields, labels, text, pivot metrics and save persistence were exercised. No private report artifacts are distributed.
- **Filter behavior:** end-to-end interaction and propagation across sources remained unverified. Configuration alone is not a passing filter test.
- **Claude Code:** configuration follows its official MCP format; the client is not installed in the development environment, so no runtime or live-report claim is made.
- **macOS/Linux and WSL:** configurations are provided; live browser connections have not been tested on those platforms.

## Reproduce local checks

```sh
python scripts/check.py
python -m unittest discover -s tests -v
python scripts/smoke_test.py
python scripts/smoke_test.py --browser-test
```

The package check scans local links and selected private-artifact patterns; it is not a comprehensive secret detector. Unit tests parse all client configurations and check browser launch invariants. The smoke test initializes the pinned server; the optional browser test operates only on a local fixture.

See the recorded results below for checks completed on this repository revision.

## Recorded results — September 21, 2026

Environment: native Windows, Python 3.12, Node.js 24.18.0, OpenCode 1.18.30, and Playwright MCP 0.0.82.

- Package structure, JSON, local documentation links, and selected private-artifact checks: passed.
- Unit tests: two tests passed, including launch contracts for eight client/platform combinations.
- MCP startup with the extension configuration: passed; 31 tools discovered.
- Isolated browser fixture: navigation, button state change, and coordinate drag passed.
- OpenCode `--pure mcp list` with the Windows configuration: `looker-browser` connected. This verifies client/server startup; it does not establish a live extension session or test report edits through OpenCode.
- Codex plugin and skill validators: passed.

Claude Code runtime, macOS/Linux runtime, and full cross-source filter interactions remain untested.

## Version 0.3 executable actions — September 21, 2026

Tested against an owner-authorized freeform training report in the Spanish Looker Studio UI, using its existing source. Private identifiers, screenshots and raw results remain outside Git.

- Created all six supported chart types through the executable action: table, scorecard, bar, pie, time series and pivot. Requested rectangles were checked, including automatic correction of initial chart sizing.
- Moved an existing chart horizontally and vertically and resized it; the resulting canvas coordinates matched the request within the documented two-pixel tolerance.
- Replaced dimension, metric, pivot-row and pivot-column fields. Tested exact-name selection, already-selected fields and duplicate chart/default-group entries.
- Set and verified rendered chart titles. Bringing the tab to the front resolved background rendering stalls encountered during development.
- Set ascending primary sorting on a bar and table and descending sorting on a pie; checked the selected field and radio state.
- After another reload, checked ascending year order in the table's rendered rows and visually in a screenshot of the bar chart. Canvas-rendered chart labels were not available as DOM text.
- Eight component IDs, titles, positions and sizes survived a report reload. A representative bar chart's dimension and metric also survived reload.
- A deliberately wrong report ID was rejected before mutation.
- Python tests cover input rejection, user-text serialization, protocol lifecycle, and browser-only/action configurations. JavaScript syntax checks passed.
- The complete stdio action server initialized and listed its Looker actions plus 31 Playwright tools. OpenCode connected to the action-server configuration on native Windows. A direct Windows Store Python launcher failed under OpenCode; the generated `cmd /c python` launcher passed.
- Live UI action bodies ran through the existing connected Playwright session. A separate fresh stdio-to-extension live inventory did not complete without a new tab connection; full live editing through that fresh connection remains unverified. Server startup alone is not claimed as that test.

These are functional tests of specific UI operations, not evidence of improved performance across smaller language models. Source reconnection, extra field slots, aggregation editing, advanced styles, filters, responsive/grouped layouts and English-locale live testing are outside the executable action coverage.
