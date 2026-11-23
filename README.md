# Shorts Generator System

Tooling for generating short-form vertical videos.

> 93 skills are implemented. See `docs/SKILL-INDEX.md` for the full list and `docs/HOW-TO-USE.md` for the pipeline.

## Getting started

1. Clone the repository.
2. Follow the setup instructions for the runtime used by the project (Python and/or Node).
3. Configure any required API keys through environment variables.

## Configuration

- Keep secrets in `.env` (or your shell/CI environment). `.env` and `.env.*` are ignored by Git.
- If configuration keys need to be documented, commit a sanitized `.env.example` with placeholder values only.
- Never commit API keys, tokens, certificates, or credential files.

## Renders

Generated media (for example `*.mp4`, `*.mov`, `*.webm`) and output directories such as `renders/` and `output/` are ignored so large video files are not uploaded.
