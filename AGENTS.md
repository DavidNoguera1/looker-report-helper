# Working on Looker Report Helper

For report work, read `skills/design-looker-report/SKILL.md` and its UI guide. For repository work, preserve the single canonical skill and shared `config/server.json`; generate client examples from that configuration.

Never include real report/Sheet identifiers, source exports, browser tokens, cookies or screenshots from private accounts. Use `private/` for local briefs and `artifacts/` for local test output. Do not modify a live report merely to test documentation changes.

Run `python scripts/check.py` and `python -m unittest discover -s tests -v` after implementation changes. Run MCP smoke tests when changing launch configuration. Record the difference between schema checks, server initialization, local browser tests, and live client/report tests in `docs/validation.md`.

Keep native client manifests distinct: Codex's plugin manifest is not a Claude Code or OpenCode plugin manifest. Offer the shared MCP and skill installation route for those clients. Publishing/remotes are a separate step requested by the repository owner.

Executable actions live in `automation/looker.js`, exposed by `automation/server.py`. Prefer these over rediscovering supported UI sequences. Never mutate application internals or rendered styles directly. Validate action inputs before browser calls, retain report guards, and verify postconditions. Run `scripts/smoke_actions.py` when changing this server. Configuration output generated with `--with-actions` contains machine-specific paths and must remain local.
