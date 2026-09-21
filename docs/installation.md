# Installation

Common requirements: Node.js 18+, npm/npx, Chrome with Playwright Extension, and permission to edit the report. Python 3.11+ is only needed for this repository's utilities. The browser extension and MCP server are separate components. Everyone connects their own Google session.

## Ready-to-copy configurations

`config/clients/` contains Windows and POSIX examples for each client, generated from `config/server.json`. You can also print them without changing any settings:

```sh
python scripts/render_config.py --client codex --platform windows
python scripts/render_config.py --client claude --platform windows
python scripts/render_config.py --client opencode --platform windows
```

Use `--platform posix` on macOS/Linux. With WSL, the locations of the browser and server matter: the original tests used native Windows, not a WSL-to-Windows browser connection.

Merge the `looker-browser` section into your existing configuration. Do not replace a file containing other servers or preferences. Use one active assistant per report.

## Codex

The MCP route does not require a marketplace. Merge `config/clients/codex.windows.toml` or `codex.posix.toml` into `~/.codex/config.toml`. The example includes a 60-second startup timeout. See the [official Codex MCP documentation](https://developers.openai.com/codex/mcp/) for configuration locations.

Alternatively, on Windows:

```powershell
codex mcp add looker-browser -- npx.cmd -y @playwright/mcp@0.0.82 --extension --browser chrome --caps vision --snapshot-boxes
```

On macOS/Linux, replace `npx.cmd` with `npx`. If using the CLI command, add `startup_timeout_sec = 60` to the server block when the initial download exceeds the default timeout.

This repository also includes `.codex-plugin/plugin.json` and `.mcp.json` for Codex plugin packaging. The public plugin configuration uses `npx`; use `plugin.windows.json` as `.mcp.json` in a local Windows packaging copy. Do not register both the packaged plugin and the manual MCP server. Native marketplace distribution is separate from this portable setup.

Start a new thread after configuration and ask the agent to read `skills/design-looker-report/SKILL.md`. To reuse the skill in other projects, copy the entire `design-looker-report` directory, including references, into your personal Codex skills directory.

## Claude Code

The Codex manifest is not a native Claude Code plugin. Use the shared MCP server and skill.

Merge `config/clients/claude.windows.json` or `claude.posix.json` into the project's `.mcp.json`. Approve project configuration if the client prompts you. In this repository, `CLAUDE.md` directs the agent to the skill. For another project, copy the entire skill directory into `.claude/skills/design-looker-report/`.

CLI alternative, native Windows:

```powershell
claude mcp add --transport stdio --scope project looker-browser -- cmd /c npx -y @playwright/mcp@0.0.82 --extension --browser chrome --caps vision --snapshot-boxes
```

On macOS/Linux, use `-- npx ...` without `cmd /c`. See [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp) for scopes and check server status with `/mcp`. Configuration does not bypass the client's own approval controls.

## OpenCode

Merge `config/clients/opencode.windows.json` or `opencode.posix.json` into your project's `opencode.json`. It registers a local server with a command array, following [OpenCode's MCP format](https://opencode.ai/docs/mcp-servers/).

```sh
opencode mcp list
```

Ask the agent to read `skills/design-looker-report/SKILL.md`. For automatic discovery in another project, copy the entire skill directory into `.opencode/skills/design-looker-report/`, following the [skills documentation](https://opencode.ai/docs/skills/).

## First connection

1. Open Chrome and a test report; sign in yourself.
2. Start your client with the MCP configuration.
3. Ask it to list browser tabs and select the intended tab in the extension dialog.
4. Ask for a screenshot and report inventory without edits.
5. In an authorized test report, change one title, verify the canvas, and reload to check persistence.

The dialog-based connection does not require sharing an extension token. If you use the optional token setting, keep its value in your local environment, never in examples or Git.

Client instructions follow official documentation. [Validation status](validation.md) separates configuration checks, server startup and live report tests.
