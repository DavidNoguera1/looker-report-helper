---
name: design-looker-report
description: Create and edit Google Looker Studio reports through the browser, configuring charts, data sources, filters, text and layout from user commands. Use for Looker Studio, not Looker LookML.
---

# Design Looker Studio reports

Use the connected `looker-browser` Playwright MCP tools to edit the real report. Read [the UI guide](references/looker-studio-guide.md) before changing chart fields, sources, pivots or controls. A mockup or configuration plan is not a saved Looker report.

Identify the authorized target and distinguish it from a reference report. Ask for a missing target/source when needed. Continue routine edits already authorized; do not treat connection to a browser as permission to edit unrelated reports, raw Sheets, sharing or publication. The user handles login, MFA and the extension's tab chooser. Do not retrieve authentication material.

Inspect a current snapshot and screenshot. Check worksheet schema, row grain, dates, percentage scale and preprocessing formulas before mapping fields. Do not invent missing metrics. Reconnecting an embedded source may invalidate existing fields; inspect every affected chart. Check whether the source is reusable before changing a shared source.

Operate visible controls using observed labels or fresh references. Browser evaluation may inspect rendered DOM and operate UI controls, but must not mutate internal application state or call undocumented mutation endpoints. Verify selection in the active panel before editing. A hidden Style panel can expose stale values. Treat every field, alias, sort or title update as a separate state transition; verify it before starting the next.

If an action times out, inspect the actual result before retrying. Change the approach only from fresh UI evidence. If a control remains unreliable, preserve completed work, identify what is unverified, and avoid claiming success from a tool return alone.

Use the worksheet at the exact chart grain. Never roll up medians into an overall median by summing or averaging them. Do not apply percent formatting that multiplies values already expressed per 100. Preserve missing values and original outliers. Label impressions separately from unique reach. State sample sizes and incomplete periods.

Verify a representative chart value against the source, chronological ordering, overflow and save persistence in view mode. Test filter selections and reset, including their effect on each source; configured fields alone do not prove propagation. Mark written analysis as static unless it actually recalculates with filters.

Return the report link, concrete changes, checks performed and unresolved limitations. Do not claim client compatibility or full report validation from a local fixture or MCP startup test.
