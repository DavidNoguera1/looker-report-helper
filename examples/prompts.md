# Example prompts

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
