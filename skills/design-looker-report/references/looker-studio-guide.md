# Practical Looker Studio editing guide

This guide records controls observed in a real Spanish-language Looker Studio session on September 21, 2026. The explanation is in English; Spanish labels are retained beside English equivalents so agents can recognize that interface. Labels and selectors may change. Verify the active panel rather than relying on remembered coordinates.

## 1. Connect and inspect the canvas

Start Playwright MCP with `--extension` to connect the user's existing Chrome session. The user signs in and selects the tab. Confirm its URL and title. **Edit (Editar)** opens the editor; **View (Ver)** returns to the reading view.

The top toolbar included Add data, Add a chart, Add a control, Theme and layout, and the Insert, Arrange and Resource menus. The right side contains component properties and available data fields. “Let's get started” / “Empecemos” means no editable component is selected.

Select the chart or text box on the canvas. If a click only enables chart interaction, use an observed edit control or double-click, then verify the property panel. Keep the tab in the foreground. Capture the screen again after scrolling or changing zoom.

## 2. Google Sheets data sources

Distinguish the spreadsheet filename from the worksheet name: a source connects to a specific worksheet. Record its row grain: publication, year, quarter, or weekday/hour.

For an existing source, open Resource and manage added data sources, then Edit the relevant source. Check whether it is embedded or reusable. Changing a shared source can affect other reports. When reconnecting is appropriate, select the file, worksheet and header settings; inspect the schema changes before Reconnect, Apply and Done.

After reconnecting, check every affected chart. Similar field names do not prove that identifiers or types were preserved. Inspect auxiliary metrics and sorting in filter controls too: they may still reference a field whose meaning changed.

## 3. Chart configuration and style

| Goal | Observed control | Verify |
| --- | --- | --- |
| Change source | Setup / Configuración → Data source / Fuente de datos | Correct worksheet and access |
| Change year, quarter or weekday | Dimension / Dimensión, or X-axis dimension | Type and grain |
| Change values | Metric / Métrica, or Y-axis metric | Source field and aggregation |
| Rename a series | Left half of field chip → Display name / Nombre visible | Label changes; source field stays correct |
| Replace a field | Right half of field chip → Search / Buscar | Do not confuse replacement with formatting |
| Change chart title | Style / Estilo → Chart title / Título del gráfico | Confirm on the canvas |
| Format numbers | Field editor → Display format / Formato de visualización | Number(2) for already-per-100 values |
| Sort chronologically | Setup → Sort / Ordenar | Field, direction and aggregation |

Build and verify one representative chart before duplicating it. Check the copy's source, dimensions, metrics, sorting and filters. Inherited properties do not automatically acquire the new meaning.

An annual totals table can display values from one row per year. A precomputed median is valid only at its original grain: reading one quarterly row is valid, but summing quarterly medians is not an overall median. Disable misleading subtotal or grand-total rows.

For a combo chart, distinguish counts, impressions and percentages, and review axis assignments. Their heights are not comparable when units or axes differ. Recheck legends and scales after replacing metrics.

## 4. Content tables

Choose identity, date, format and performance fields. Sort by the actual ranking metric and check the first and last records. A numeric field may be configured as a dimension, affecting aggregation options despite its numeric display.

Style controls included headers, text wrapping, automatic height, horizontal scrolling, font sizes and pagination. Avoid letting long descriptions consume the table. Review unnecessary time components in dates, excessive decimals and columns outside the visible width. If publication links are required, add the existing URL field and test a link before claiming it works.

## 5. Pivot tables and heatmaps

A useful setup is **rows = hour**, **columns = weekday**, **metrics = median and publication count**. In Style, select each metric to set its heatmap appearance and color. Keep labels and units readable.

1. Choose row and column fields.
2. Replace metrics one at a time and verify their source.
3. Assign short labels such as `E (%)`, `Imp.` and `n`.
4. Configure sorting after field and label changes.
5. Sort hours numerically. Sort weekdays by weekday number. With multiple hourly rows per day, **MIN(weekday_number)** avoids a sum that depends on how many populated slots each day has.
6. Check the rendered order. A configured sort is not proof of a saved visual result.
7. Disable grand totals of medians and percentages.

If the source includes empty rows for every hour, a `publication_count > 0` filter can remove empty slots without dropping actual publications. Days without records may disappear; explain this. Use a minimum-sample engagement field when the source provides one. Do not turn insufficient-sample values into zero.

Maximum row count and chart height are different settings. A table configured for 24 rows may still show only some through a scrollable viewport. Review exported PDFs separately if required; an interactive view does not prove that the PDF includes every row.

## 6. Filters and scope

A dropdown control included Control field, Default selection, Metric, Show values, Sort and a maximum option count. Use the actual year or quarter as its control field. An inherited auxiliary metric may be inappropriate; a record count is often clearer than a complete-period indicator.

To create a chart filter: Add a filter → Create a filter → Filter name → Include/Exclude → field → condition → value → Save. To reuse one, select it from the existing filter list.

Test a control through observable outcomes:

- The menu offers the expected values.
- Selecting a known period changes the intended charts to source-verified results.
- Its effect on other sources and the ranked table is understood.
- Reset restores the initial view.

Do not promise global filtering merely because different sources have identically named columns. Verify scope or group related controls and charts when supported by the observed UI. Written commentary is static unless implemented otherwise; label its cutoff date. Full filter interaction testing remained incomplete in the original session and must not be treated as demonstrated behavior.

## 7. Text, layout and long pages

Double-click a text box to activate editing. Replace the content, leave the field and inspect the result. Keep headings short and explain units, cutoff dates and incomplete periods. Do not copy conclusions from a previous social network when adapting a template.

DOM enumeration order may differ from vertical placement. In the original session, two commentary boxes were listed in a different order from their visual sections. Match explanations by content and position, not only by an index.

Preserve a long page when requested. Prefer observed Arrange alignment/distribution commands, numeric size/position controls, or visible handles. Check margins, contrast, font consistency, clipped text and overlaps. Successfully editing fields does not prove a good layout.

## 8. Automation details that prevent mistakes

Observed titles were `div.chart-title` with `role="heading"`, not `h2`. The properties panel was `article.property-panel`. Observed `data-webdriver-cell-key` values included:

| Key | Observed purpose |
| --- | --- |
| `metrics` | Chart metrics |
| `actionConceptList` | Chart or table dimensions |
| `pivotTableRowDimensions` / `pivotTableColDimensions` | Pivot rows / columns |
| `columnSortColumn0` / `columnSortDir0` | Column sort field / direction |
| `rowRowsCount0` | Maximum pivot row count |
| `chartTitleText` | Title input in Style |
| `controlField` / `filterMetric` | Control dimension / auxiliary metric |

These are observed implementation details, not a stable API. Reinspect them. In field chips, `.right-half` opened replacement selection; `.left-half` opened field properties. Identify the active dialog instead of acting on an ambiguous Search or Display name input.

Updates are asynchronous. Rapidly chaining selection, replacement, renaming, sorting and navigation sometimes produced successful tool returns while losing intermediate changes. Verify each transition before the next. A hidden Style tab can retain the previous component's inputs; open it before using its title as evidence of selection. After a timeout, inspect what actually happened before retrying.

In PowerShell, sending Unicode JSON through default-encoded stdin replaced accented characters with question marks. Use explicit UTF-8 or serialize non-ASCII characters as JSON Unicode escapes. Keep user-provided text out of unescaped shell commands.

References and screenshots become stale after navigation, scrolling or zoom. Coordinate interactions and focus were not uniformly reliable. Use observed UI controls; never replace them with undocumented save endpoints or internal state mutations.

## 9. Verify and deliver

Return to View and inspect titles, values, order, legends and controls. Reload to verify persistence. Resolve pending saves or network failures before navigating away. If delivering a PDF, export and inspect that file too.

Report edits, numerical checks, visual checks and limitations separately. MCP startup, a local fixture and a live report are different levels of evidence. Keep an accurate list of anything still unverified.
