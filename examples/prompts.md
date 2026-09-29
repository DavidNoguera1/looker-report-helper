# Example prompts

## Complete chart workflow (version 0.4)

> Connect to my authorized Looker report and read the action recipes. Discover the annual source and its exact year/impressions fields. Use `looker_build_chart` to create an annual impressions bar chart with the ocean palette and chronological sorting. Choose free space on the page, preserve the returned component ID, and verify values and persistence.

## Sources and colors

> List the sources available to the selected chart. Before switching it to the monthly source I specify, check the intended row grain and discover its fields. Remap the chart and verify its date range, sorting and filters. Report any dataset access problem.

> Inspect the selected chart's available color properties. Set its background to #f0fdfa, title to #134e4a and first enabled series to #0d9488 if those controls exist. Verify the chart after reloading.

## Resume a partial workflow

> Inspect the partial result and the current canvas. Resolve the reported issue, then retry the same `looker_build_chart` arguments and request ID. Reuse the saved component; do not create a duplicate to retry.

## Use the executable actions

"Use `looker_inventory` on the report I authorize. Create a bar chart at x=40, y=180, width=500, height=260 with `looker_create`. Use the returned ID to set the year dimension, impressions metric and title with the Looker actions. Inspect the source first and verify the chart after reloading."

"Move the chart titled Annual impressions to x=600, y=180 and resize it to 500 by 260 canvas pixels. Find its current component ID using `looker_inventory`, then use `looker_layout`."

These prompts require the action-server setup; the browser-only configuration does not expose `looker_*` tools.

## Inspect a report

> Read this repository's Looker skill. Connect to the tab I select and inventory its sources, charts and controls without editing yet.

## Adapt a template

> Use the reference report only as inspiration. Edit the target I provide using my processed spreadsheet. Keep one long page, separate posts and newsletters, and verify source granularity and formulas first.

## Change a metric

> In the quarterly impressions chart, replace both series with median clicks for posts and newsletters. Update the title, preserve chronological order, and compare one displayed value with the spreadsheet.

## Explore hourly patterns

> Create a weekday-by-hour heatmap with median engagement and publication count. Use the minimum-sample field if the source provides one. Keep original values and explain missing cells.

## Test filters

> Select a known quarter, record which charts change, and verify their values. Restore the original view. Do not assume the filter propagates between different sources.

## Review layout

> Align the three annual charts, standardize titles and legends, and place commentary beside the correct section. Keep the long page. If exporting a PDF, check for clipped rows too.
