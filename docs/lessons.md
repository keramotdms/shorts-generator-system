# Lessons Learned

## 2026-11-22 — Setup and tooling

- **GitHub CLI MSI install was cancelled at the UAC prompt.**
  Lesson: when administrator approval is unavailable, use the portable ZIP build under the user profile instead.

- **Expected `python` to be available, but Windows only had the Microsoft Store stub.**
  Lesson: verify a real interpreter with `python --version` before writing/running Python scripts. Ask before installing Python.

- **First `git push` hung on a Git Credential Manager dialog.**
  Lesson: GitHub Desktop's stored token can be copied into Git's credential helper. Use `GIT_TERMINAL_PROMPT=0` to avoid hangs.

- **Skill-relative path mismatch:** `shorts-script-writer` saved `scripts/latest_script.json` inside its own skill folder, while `shorts-voiceover-captions` expects it at the repo root.
  Lesson/fix planned: generated project data should live under `projects/<project>/<stage>/`, not inside skill folders. Migrate the existing script when the Asset & Version Manager skill is built.

## Rules for future mistakes

- Log the mistake, why it happened, and the fix here immediately.
- Never install a tool or package without telling the user what and why, and getting approval.
- Build one skill at a time; show the test steps and wait for OK before continuing.
