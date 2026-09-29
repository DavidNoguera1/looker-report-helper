# Distribution options

Checked September 29, 2026. The public GitHub repository is the source of truth. The skill can be installed directly from GitHub. The Awesome OpenCode submission was withdrawn at the project owner's request; skills.sh search indexing remains unverified.

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

A subsequent project-scoped installation with `--copy --yes` succeeded from the public repository. The installed skill and both reference files matched the canonical contents. This verifies distribution of the instructions, not setup of the MCP server. A subsequent `skills find` query did not yet return the skill; search/leaderboard visibility is unverified. The CLI's installation telemetry is described in its [documentation](https://www.skills.sh/docs/cli).

## 2. Official MCP Registry: package distribution later

The [MCP Registry](https://modelcontextprotocol.io/registry/quickstart) publishes server metadata rather than hosting the implementation. Our local Python server could use its [PyPI package route](https://modelcontextprotocol.io/registry/package-types), or a suitable supported bundle, after packaging and installation tests.

This repository currently uses a clone plus a generated absolute-path launch command. Before Registry submission, create and publish a versioned installable package, verify its ownership metadata, add a Registry `server.json` and authenticate with the publisher CLI. The existing `config/server.json` is our Playwright launch configuration; it is **not** the Registry manifest.

Keep execution local: this integration needs the user's Chrome session. A directory listing does not turn it into a hosted Google API or remove the extension connection step.

## Withdrawn submission

[Awesome OpenCode PR #784](https://github.com/awesome-opencode/awesome-opencode/pull/784) was closed without merging on September 29, 2026, at the project owner's request. The project is not listed there through that submission. The closed PR remains part of GitHub's public history.
