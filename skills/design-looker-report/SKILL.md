---
name: design-looker-report
description: Create and edit Google Looker Studio reports through the browser, configuring charts, data sources, filters, text and layout from user commands. Use for Looker Studio, not Looker LookML.
---

# Design Looker Studio reports

Use the connected `looker-browser` MCP tools to edit the real report. A mockup or configuration plan is not a saved Looker report.

When `looker_*` tools are available, read [action recipes](references/action-recipes.md) and use them for supported operations. Start with `looker_inventory`, then inspect the relevant component. Discover source names with `looker_sources` and fields with `looker_fields`; do not infer them from another report. Prefer `looker_build_chart` for a complete chart: it sequences source, field, title, layout, sorting and palette operations. Supply a stable `request_id`; retry identical arguments to resume a partial result. For edits, include the existing `component_id`. Do not change the request ID to retry an uncertain insertion. Use `looker_inspect_style` and `looker_set_color` for individual colors. Every action requires the authorized report ID.

For unsupported operations, read [the UI guide](references/looker-studio-guide.md) and inspect fresh browser evidence. Compact mode exposes only basic browser inspection plus Looker actions; advanced UI work needs the full server mode. Do not claim an unsupported operation was completed. These tools automate UI sequences, not source/aggregation analysis or final reload verification.

Identify the authorized target and distinguish it from a reference report. Ask for a missing target/source when needed. Continue routine edits already authorized; do not treat connection to a browser as permission to edit unrelated reports, raw Sheets, sharing or publication. The user handles login, MFA and the extension's tab chooser. Do not retrieve authentication material.

Inspect a current snapshot and screenshot. Check worksheet schema, row grain, dates, percentage scale and preprocessing formulas before mapping fields. `looker_set_source` switches one chart to an existing source; it does not reconnect the shared source. Source selection and listed fields do not prove permission to read its data. After switching, remap fields and review date range, sort, filters and calculations. Reconnecting a source may affect many charts or reports; read the guide and inspect that scope first.

Operate visible controls using observed labels or fresh references. Browser evaluation may inspect rendered DOM and operate UI controls, but must not mutate internal application state or call undocumented mutation endpoints. Verify selection in the active panel before editing. A hidden Style panel can expose stale values. Treat every field, alias, sort or title update as a separate state transition; verify it before starting the next.

If an action times out, inspect the actual result before retrying. Change the approach only from fresh UI evidence. If a control remains unreliable, preserve completed work, identify what is unverified, and avoid claiming success from a tool return alone.

Use the worksheet at the exact chart grain. Never roll up medians into an overall median by summing or averaging them. Do not apply percent formatting that multiplies values already expressed per 100. Preserve missing values and original outliers. Label impressions separately from unique reach. State sample sizes and incomplete periods.

Verify a representative chart value against the source, chronological ordering, overflow and save persistence in view mode. Test filter selections and reset, including their effect on each source; configured fields alone do not prove propagation. Mark written analysis as static unless it actually recalculates with filters.

Return the report link, concrete changes, checks performed and unresolved limitations. Do not claim client compatibility or full report validation from a local fixture or MCP startup test.
