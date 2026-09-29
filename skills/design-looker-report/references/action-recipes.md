# Action recipes

Use these when the MCP connection exposes `looker_*` tools. Examples use placeholders: obtain the real report ID from the authorized URL and component IDs from inventory. Never guess IDs or source field names.

## Choose the shortest supported route

| User request | Tool sequence |
| --- | --- |
| Review existing charts | `looker_inventory` → `looker_inspect` |
| Review other sources | `looker_sources`; for an authorized chart source switch, `looker_set_source` → `looker_fields` |
| Create/configure a chart | Discover names → `looker_build_chart` → visual/value/reload checks |
| Move or resize a chart | `looker_inventory` → `looker_layout` |
| Change one field or title | `looker_inspect` → `looker_set_field` or `looker_set_title` |
| Change colors | `looker_inspect_style` → `looker_set_color` |
| Apply a preset to a complete chart | `looker_build_chart` with `palette` and existing `component_id` |

If the page has no charts, create one seed chart with `looker_create`, inspect its source/fields, then pass its ID to `looker_build_chart`. Reuse that chart. Attaching the report's first data source may require the full browser tools.

## Sources and fields

`looker_sources` takes `report_id` and `component_id`. It returns exact names with `scope: added|available|unknown`. A listed source can still lack dataset access. Duplicate exact names stop `looker_set_source` with `AMBIGUOUS_SOURCE`; inspect the UI rather than selecting an arbitrary match.

`looker_fields` reads the **current chart source**, without replacing a field:

```json
{"report_id":"YOUR_REPORT_ID","component_id":"cd-FROM-INVENTORY","slot":"metric","query":"impressions","limit":20}
```

Use `dimension`, `metric`, `pivot_row` or `pivot_column` as appropriate. `has_more: true` means the virtualized list was limited; narrow the query. An empty list is a valid result. `type_numeric`, `type_datetime` and other icons are UI hints, not a complete source schema. Validate date semantics, row grain and aggregation from the source/brief.

Switching a component's source can map old fields to unintended new ones. Inspect its resulting fields, then explicitly select the intended names. The tools do not edit spreadsheet data or the shared connector.

## Complete chart in one call

Call `looker_build_chart` with exact discovered names:

```json
{
  "report_id":"YOUR_REPORT_ID",
  "request_id":"annual-impressions-01",
  "type":"bar",
  "title":"Annual impressions",
  "source":"Example annual source",
  "dimension":"Year",
  "metric":"Impressions",
  "sort_field":"Year",
  "sort_direction":"ascending",
  "palette":"ocean",
  "x":40,"y":180,"width":480,"height":260
}
```

- Add `component_id` to update an existing chart of the same type.
- Omit all four geometry properties to preserve an existing chart's rectangle or auto-place a new chart. Auto-placement searches for free space on the current page; it never grows the page. An explicit rectangle may intentionally overlap other components.
- Types: `table`, `bar`, `scorecard`, `pie`, `time_series`, `pivot`. Scorecards require only `metric`; other types require `dimension`; pivots also require `column_dimension`.
- Presets: `light`, `dark`, `ocean`. Only supported properties are changed; `palette_applied` records which ones. Presets set series index zero when enabled, not every category or conditional-formatting rule.
- Sorting is supported for tables, bars and pies. Omit sorting for other types.

The server stores a local checkpoint before insertion and keeps the new ID. For `status: partial`, read `failed_step`, `error` and `component_id`. Retry **identical arguments and request_id** after resolving a transient issue. To change the design, use a new request ID **and the existing component ID**. A changed request with the same ID is rejected. An uncertain insert is adopted only when one new matching rectangle is found; otherwise it stops for inspection without inserting again.

Do not equate `status: complete` with correct analytical results: inspect values, aggregation, dates, filters, clipping and order. Reload and verify persistence. The workflow returns `saved_persistence_verified: false` and `numerical_accuracy_verified: false` because it does not perform those separate checks.

## Individual colors

Call `looker_inspect_style` first. Use a property actually returned by the selected chart:

```json
{"report_id":"YOUR_REPORT_ID","component_id":"cd-FROM-INVENTORY","property":"background","color":"#f0fdfa"}
```

Available properties can include `background`, `title`, `text`, `border`, `legend`, `plot_background`, `table_header`, `table_header_text`, `table_even`, `table_odd`, `axis`, `x_labels`, `y_labels`, `grid`. For `property: series`, use an enabled zero-based `series_index` returned by inspection (default 0). Only opaque six-digit hex colors are accepted. The action operates the color picker and verifies its swatch; check the resulting chart visually and after reload.

## Errors that change the next action

| Error/result | Next action |
| --- | --- |
| `WRONG_REPORT`, `WRONG_PAGE`, `NOT_EDIT_MODE` | Open the authorized report, original page and editor before resuming. |
| `SOURCE_NOT_FOUND`, `AMBIGUOUS_SOURCE`, dataset access error | Inspect sources/permissions. Do not bypass access or substitute a different dataset. |
| `FIELD_NOT_FOUND`, `has_more` | Search the selected source with a narrower query; verify its meaning. |
| `UNSUPPORTED_COLOR`, `SERIES_DISABLED` | Inspect available style controls and valid metrics. |
| `CREATION_UNCERTAIN` | Inventory and inspect the canvas; never blindly create again. |
| `NO_SPACE` | Choose an explicit rectangle or add space through supported UI operations. |
| `OPEN_DIALOG` | Inspect and finish the existing dialog before another edit. |

Compact mode exposes 13 Looker tools and four browser tools (tabs, navigation, snapshot, screenshot). It reduces tool choices; it does not add unsupported features or prove that every language model can use MCP reliably.
