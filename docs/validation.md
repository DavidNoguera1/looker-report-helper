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
