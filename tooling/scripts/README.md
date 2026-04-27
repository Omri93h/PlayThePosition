# tooling/scripts

Helper scripts and automation hooks live here.

Current foundation commands:

- `pnpm run build` checks build scripts in workspace packages.
- `pnpm run lint` runs Prettier checks for JS/TS/JSON/MD workspace files.
- `pnpm run test` runs JS workspace tests, including the e2e smoke test.
- `pnpm run lint:api` runs Ruff for the FastAPI service.
- `pnpm run test:api` runs Pytest for the FastAPI service.
- `pnpm run check` runs the foundation quality checks together.

Future examples:

- contract generation
- OpenAPI export
- test dataset validation
- CI helper scripts
