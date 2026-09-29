# Distribution options

Checked September 29, 2026. The public GitHub repository is the source of truth. These are discovery/submission routes, not claims that a third-party listing has been accepted.

## 1. skills.sh: distribute the reusable skill

Recommended first for users of OpenCode, Claude Code and Codex. Skills are hosted in GitHub repositories; the directory tracks installations through its CLI rather than requiring a manual listing submission. See the [official listing FAQ](https://www.skills.sh/docs/faq).

The CLI successfully discovered `design-looker-report` from this public repository:

```sh
npx skills add DavidNoguera1/looker-report-helper --list
```

Install the instructions for OpenCode:

```sh
npx skills add DavidNoguera1/looker-report-helper --skill design-looker-report --agent opencode
```

Use `--agent claude-code` or `--agent codex` for those clients. These options are documented in the [official Skills CLI repository](https://github.com/vercel-labs/skills).

**The skill install does not start or configure the MCP server.** Users must also clone this repository, install the prerequisites and follow [action-server setup](actions.md). The browser extension alone does not connect an agent. Do not advertise the instructions-only installation as a complete working Looker connection.

The discovery check is not an installation or proof of a live leaderboard listing. The CLI's installation telemetry is described in its [documentation](https://www.skills.sh/docs/cli); this project does not generate artificial installs to influence rankings.

## 2. Awesome OpenCode: list the complete integration

Recommended for reaching OpenCode users with the MCP server, setup guide and skill together. OpenCode's [official ecosystem page](https://opencode.ai/docs/ecosystem/) links this community directory.

[Contribution instructions](https://github.com/awesome-opencode/awesome-opencode/blob/main/contributing.md) require a YAML entry under the appropriate `data/` category and a pull request. Use **`data/projects/looker-report-helper.yaml`**: this project is an MCP integration with a portable skill, not a native JavaScript OpenCode plugin. A prepared [YAML entry](distribution/awesome-opencode.yaml) is included here.

The repository must be public, recently maintained, relevant, unique and include the required metadata. Maintainers review submissions before merging. The prepared entry has not been submitted.

Suggested pull request description:

> Add Looker Report Helper to projects. It connects OpenCode to the user's Google Looker Studio browser session through a local MCP action server and reusable skill. The repository includes setup instructions, executable chart/source/color workflows and a validation record that separates model trials from server startup checks.

## 3. Official MCP Registry: package distribution later

The [MCP Registry](https://modelcontextprotocol.io/registry/quickstart) publishes server metadata rather than hosting the implementation. Our local Python server could use its [PyPI package route](https://modelcontextprotocol.io/registry/package-types), or a suitable supported bundle, after packaging and installation tests.

This repository currently uses a clone plus a generated absolute-path launch command. Before Registry submission, create and publish a versioned installable package, verify its ownership metadata, add a Registry `server.json` and authenticate with the publisher CLI. The existing `config/server.json` is our Playwright launch configuration; it is **not** the Registry manifest.

Keep execution local: this integration needs the user's Chrome session. A directory listing does not turn it into a hosted Google API or remove the extension connection step.
