# Contributing

Issues and pull requests are welcome.

- Every endpoint and field used by a tool must exist in the Pinlyx REST API (`https://api.pinlyx.com/v1`). Do not add fields that are not documented there.
- Keep dependencies minimal and the host fixed to `api.pinlyx.com`.
- Run `python -m pytest tests` before opening a pull request. Tests must stay offline.
- Bump `version` in `manifest.yaml` and add a line to `CHANGELOG.md` for any change that ships in the package.
