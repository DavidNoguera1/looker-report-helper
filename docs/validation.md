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

## Version 0.4 sources, colors and workflows — September 29, 2026

Environment: native Windows, Python 3.12, Node.js 24, Chrome, Spanish Looker Studio and the pinned Playwright MCP 0.0.82. Tests used an owner-authorized training report. Private IDs, source names, screenshots, relay messages and results are excluded from Git.

- The installed v0.3 plugin's native MCP connection successfully listed browser tabs and ran inventory, inspection and field actions. This resolves the previous session's unverified connected-stdio inventory boundary.
- New v0.4 action bodies ran through that connected browser tool. The actual Python `looker_build_chart` implementation and server dispatcher were exercised with a local file relay to the same browser session. This tests workflow behavior in the live UI; it is not a fresh v0.4-client end-to-end editing test.
- Listed added and available sources, including duplicate names. Switched a chart to another existing source, inspected its numeric field metadata and restored the original source/fields. A sample source could be selected but lacked dataset access; selection is explicitly not reported as data validation.
- Duplicate and nonexistent source names were rejected, leaving the original source selected. Field discovery returned bounded results with `has_more`, exact matches and an empty list for an unmatched search. The empty-list test exposed and fixed a wait for a nonexistent virtual viewport.
- Custom hex colors, existing saved colors and already-matching swatches were exercised. Verified bar series/background/title colors, table header/header-text/even/odd colors, and scorecard background/title/text. An unsupported property was rejected.
- A complete bar update restored the intended source, preflighted field names, set dimension/metric/title/sort and applied the ocean palette.
- A complete workflow created a scorecard at a specified rectangle, set its source/metric/title and applied the light palette. Repeating identical arguments reused the same component ID without another insert. Nine total components remained after reloading.
- After reload, inspected the bar's source, fields and colors, the table's colors, and the new scorecard's source, metric, title, geometry and colors. Visually checked the bar/table styling and ascending years. The new scorecard's displayed value matched the existing same-metric scorecard; this is consistency evidence, not an independent audit of source calculations.
- Unit tests cover invalid input, UTF-8 stdin under a forced Windows code page, configuration contracts, checkpoint replay, recovery after a lost insert response, refusal to recreate an uncertain insert, field preflight, changed request IDs, original-page guards and collision-free auto-placement. Auto-placement and timeout recovery were tested with a simulated adapter; live creation used explicit geometry.
- Full MCP startup exposed 13 Looker + 31 browser tools. Compact startup exposed 13 Looker + four browser tools and rejected a non-exposed raw-code tool call. Neither startup test edited the report.
- All 16 unit tests, JavaScript syntax, public package/link checks, Codex plugin validation and skill validation passed. OpenCode `--pure mcp list` connected using the generated compact Windows configuration; this is a startup test, not a Big Pickle report-editing run.

Live tests do not cover every color property/chart-type combination, the dark preset, English UI, aggregation editing, field addition, source reconnection, date-range mapping, advanced formatting, filters or responsive/grouped layouts. Big Pickle, Claude Code and other smaller-model agent runs remain untested. Fewer exposed tools and scripted workflows are design choices; comparative speed, cost and success-rate improvements have not been measured.
