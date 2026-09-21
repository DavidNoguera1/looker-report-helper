# Contributing

The goal is verifiable report editing with clear limitations. Document observed controls without presenting internal selectors as a stable API.

1. Create a branch for the change.
2. Keep server configuration in `config/server.json`; regenerate client examples using `scripts/render_config.py` when it changes.
3. Update the canonical skill and guide rather than maintaining divergent client-specific copies.
4. Run `python scripts/check.py` and `python -m unittest discover -s tests -v`.
5. For launch changes, run `python scripts/smoke_test.py`. Use `--browser-test` for an isolated fixture and your own authorized test report for live editing.
6. Record the client, operating system, versions and exact test scope in `docs/validation.md`.

Examples must not contain real report data. Issues should include reproduction steps, the affected control and a synthetic example. Review screenshots before sharing them.

## Publishing

Review `git status`, `git ls-files`, the license and commit metadata before pushing. Use the owner's chosen account and remote. Authenticate through Git or the client application rather than pasting credentials into chat.

Keep `private/`, account screenshots, data exports and secret-bearing settings out of Git. Native marketplace distribution and additional client tests can be added in later releases.
