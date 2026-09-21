# Executable Looker actions

Version 0.3 adds a small MCP server with deterministic UI operations. The agent supplies a chart type, field name or rectangle; the implementation locates the controls, performs the UI events and checks the result. The original Playwright tools remain available for unsupported operations.

## Install the action server

Clone this repository, install Python 3.11+, Node.js and Playwright Extension, then generate a configuration **on the computer that will run it**:

```sh
python scripts/render_config.py --client codex --platform windows --with-actions
python scripts/render_config.py --client claude --platform windows --with-actions
python scripts/render_config.py --client opencode --platform windows --with-actions
```

Use `--platform posix` on macOS/Linux. Merge the generated `looker-browser` entry into your client's configuration, replacing its previous direct Playwright entry. Do not register both copies. This output contains local absolute paths; do not commit it. Moving the clone or Python installation requires regenerating it.

The action server starts the pinned Playwright MCP dependency and exposes both tool sets through one connection. Open a fresh agent session, select the report in the extension dialog and ask it to list its `looker_*` tools. A connection dialog may appear for each new server session. No token needs to be shared.

The portable `.mcp.json` and static examples retain the browser-only setup. Installing those alone does **not** enable the new actions. For a local Codex plugin packaging copy, generate `--client plugin --with-actions` and use its output as that copy's `.mcp.json` before installing it.

## Tool contract

Every action requires `report_id`, taken from the authorized report URL. The active tab must match that report. Coordinates use the freeform canvas origin, not screen pixels; zoom is measured at execution time. Inventory covers the current page only.

| Tool | Inputs besides report_id | Result |
| --- | --- | --- |
| `looker_inventory` | None | Current component IDs, chart types, titles, selection and rectangles; page dimensions |
| `looker_inspect` | `component_id` | Selects the component and reads data source and field/property slots |
| `looker_create` | `type`, `x`, `y`, `width`, `height` | Creates one chart, adjusts its initial size and returns its ID plus verification flags |
| `looker_layout` | `component_id`, `x`, `y`, `width`, `height` | Moves and resizes the existing component and checks the resulting rectangle |
| `looker_set_field` | `component_id`, `slot`, `field`, optional zero-based `index` | Replaces an existing field and checks its chip label |
| `looker_set_title` | `component_id`, `title` | Enables the title, writes it and checks rendered text |
| `looker_set_sort` | `component_id`, `field`, `direction` | Sets the primary sort on a table, bar or pie; direction is `ascending` or `descending` |

Chart types: `table`, `scorecard`, `bar`, `pie`, `time_series`, `pivot`. Field slots: `metric`, `dimension`, `pivot_row`, `pivot_column`. Slots must already exist in that chart. Exact source field names are required. These operations do not choose aggregations, add extra field slots or reconnect sources.

## Example: a bar chart without rediscovering the UI

1. Run `looker_inventory` and inspect an existing chart to establish the current source and field names.
2. Call `looker_create` with the authorized report ID and this geometry:

```json
{"type":"bar","x":40,"y":180,"width":500,"height":260}
```

3. Take `component.id` from the response. Replace its `dimension` with the exact year field and its `metric` with the exact impressions field using two `looker_set_field` calls.
4. Set its title with `looker_set_title`.
5. Inspect the chart, check aggregation and sorting, compare a value with the source, then reload and inventory again to check persistence.

The agent still decides which metric, source and chart answer the user's question. The repetitive UI sequences are now code, rather than instructions for the model to reconstruct.

## Implementation details

- `automation/looker.js` contains the operations and the observed selector map.
- `.ng2-canvas-container` provides canvas dimensions and zoom scale.
- Direct `.lego-component-repeat` children provide rendered position and size; the inner `.lego-component` has a `cd-*` component identifier. These are read from the DOM, never invented or stored in public examples.
- Insert menu items are identified by `mat-icon[data-mat-icon-name]`, scoped to `role=menuitem`. Toolbar/tab labels currently cover English and Spanish; Spanish was tested live.
- Selection uses mouse events and verifies exactly one selected component.
- Creation dispatches mouse events to the canvas and document. Resizing uses the selected component's bottom-right handle. Movement uses Shift+arrow UI events, observed to move one canvas pixel; normal arrows can snap to a grid.
- Field replacement uses `data-webdriver-cell-key`, `.right-half`, the overlay search box and an exact `.display-name` match. It waits for the new field label.
- Pie charts use `pieMetric` instead of `metrics`; the action maps this automatically. If a slot already has the requested label it returns `unchanged: true`. Otherwise the field picker prefers the exact match in the Default group, avoiding duplicate chart-field aliases. Multiple source matches stop without guessing.
- Sorting uses `sortConcept1` / `sortDir1` for tables and `sortConcept` / `sortDir` for bars and pies. Radio values `0` and `1` were observed for ascending and descending. Control verification is separate from checking the actual rendered order.
- Leftover field pickers are dismissed through their backdrop before another action. An open dialog stops the action rather than discarding dialog edits.
- Titles use the `chartTitleShowTitle` switch and `chartTitleText` input, then verify `.chart-title` on the canvas.

No Angular object access, private save endpoints, direct component-style assignments or authentication extraction are used. These selectors are observed implementation details, not a supported Google API.

`automation/server.py` validates arguments, exposes tool schemas, serializes actions and forwards browser tools. `automation/bridge.py` speaks newline-delimited JSON-RPC to the official Playwright server. Its optional loopback HTTP route is for development. See the [MCP transport specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) and [Playwright MCP](https://github.com/microsoft/playwright-mcp).

## Failures and boundaries

- A creation timeout can occur after the component was added. Refresh inventory before retrying; creation is not idempotent.
- If size adjustment fails after creation, the result contains the new component ID and `geometry_verified: false`. Continue from that component.
- Geometry tolerance is two canvas pixels because scaled mouse events may round. Very large keyboard moves may be slow.
- A field label check does not verify aggregation, numerical correctness, source access, filters or saved persistence.
- Each action brings the authorized tab to the front. Keep Chrome available; background rendering can otherwise leave a switch updated while its dependent controls have not rendered.
- Unsupported locales, responsive layouts, grouped components, locked components and application UI changes may require browser inspection. Nested/grouped component editing is not implemented.
- Actions use the current default source. Source selection, additional metrics, custom styles, filters, text boxes and multi-page report composition still use the browser tools and guide.
- MCP calls run serially. Closing or cancelling a client does not prove a partially completed UI action was rolled back.

## Tests

```sh
python -m unittest discover -s tests -v
python scripts/check.py
node --check automation/looker.js
python scripts/smoke_actions.py
```

For an authorized test report, `python scripts/smoke_actions.py --report-id YOUR_REPORT_ID` also checks a read-only inventory through the full server chain. The extension may request a tab selection. Real report mutations are never part of the default test suite.
