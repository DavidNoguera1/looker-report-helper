# Troubleshooting

| Symptom | Check and next step |
| --- | --- |
| No clients are currently connected | Start the MCP server from your client with `--extension`, then request the tab list. |
| Extension not found | Check that the extension is installed in the open Chrome profile. The user selects the tab and completes sign-in. |
| Slow server startup | The first npx run may download packages. Check Node/npm, networking and the client's startup timeout. |
| npx fails on Windows | Use the Windows configuration for your client; a .cmd launcher is not a POSIX executable. |
| The panel displays “Let's get started” | Select a component and confirm that its properties are active. |
| Clicking does not select the intended component | Check focus, zoom, editor mode and a fresh screenshot. Tool success alone does not prove selection. |
| Multiple Search or Display name inputs | Identify the active popup and close earlier popups before continuing. |
| Changes disappear | Verify each state transition before the next mutation. Read it back and reload after saving. |
| Weekdays are out of order | Sort by weekday number using MIN when multiple hourly rows exist. Recheck after renaming metrics. |
| Percentages are 100 times too large | The source may already be expressed per 100. Use Number(2) and a (%) label rather than scaling it again. |
| A filter does not affect everything | Check source, control field, grouping and scope against a known period. |
| A PDF loses rows | Check table height and scrolling; verify the exported file separately. |
| Accented text becomes ? | Use explicit UTF-8 for PowerShell JSON input, or JSON Unicode escapes. |

Console warnings do not automatically make a report invalid; an error-free screen does not prove numerical correctness either. Check values, persistence and behavior. Do not paste private-session logs into public issues: they may contain report URLs and data.

If a control remains unreliable after inspection and an evidence-based adjustment, preserve verified changes and state what remains untested. Do not replace UI editing with undocumented backend mutations.
