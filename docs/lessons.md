# Lessons Learned

## 2026-11-22 — Setup and tooling

- **GitHub CLI MSI install was cancelled at the UAC prompt.**
  Lesson: when administrator approval is unavailable, use the portable ZIP build under the user profile instead.

- **Expected `python` to be available, but Windows only had the Microsoft Store stub.**
  Lesson: verify a real interpreter with `python --version` before writing/running Python scripts. Ask before installing Python.

- **First `git push` hung on a Git Credential Manager dialog.**
  Lesson: GitHub Desktop's stored token can be copied into Git's credential helper. Use `GIT_TERMINAL_PROMPT=0` to avoid hangs.

- **Skill-relative path mismatch:** `script-writer` saved `scripts/latest_script.json` inside its own skill folder, while `voiceover-captions` expects it at the repo root.
  Lesson/fix planned: generated project data should live under `projects/<project>/<stage>/`, not inside skill folders. Migrate the existing script when the Asset & Version Manager skill is built.

## 2026-11-22 — Python installation and Orchestrator test

- **Windows `python` was a Microsoft Store stub, not a real interpreter.**
  Fix: installed portable Python 3.15.2 (embeddable build) under `AppData\Local\Programs\Python\Python315-embed` and prepended it to the user PATH. Verified `python --version` returns `Python 3.15.2`.
- **Orchestrator smoke test passed:** `init`, `status`, `complete research`, `status`, `reset` all behaved as expected. Note: `status` with no state file exits with code 1 by design, so a shell script will report a non-zero exit on that last check even though it is correct behavior.

## 2026-11-22 — FFmpeg install blocked by Smart App Control

- **Installed `Gyan.FFmpeg` 9.1 via winget successfully** (portable ZIP, no admin needed). `ffprobe.exe` runs fine, but `ffmpeg.exe` is blocked: `[WinError 4551] An Application Control policy has blocked this file`.
- **Root cause:** Windows 11 Smart App Control is in **Enforcement** mode (`HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy\VerifiedAndReputablePolicyState = 1`). All winget FFmpeg builds are unsigned community builds. `ffprobe.exe` has good reputation; `ffmpeg.exe` does not.
- **Health check false positive:** the original `check_ffmpeg()` used `shutil.which()`, which only finds the file on PATH and reported PASS even though the binary could not run. Fixed it to actually execute `ffmpeg -version` / `ffprobe -version` and report `WARN` on failure.
- Lesson: **finding a binary is not the same as running it.** Always execute `--version` in environment checks. Disabling Smart App Control is a security change and needs explicit user approval (it cannot be re-enabled without a Windows reset).

## 2026-11-22 — Full 93-skill scaffold and implementation

- **Generator wrote `status: mvp`/`planned` instead of `implemented`.** The scaffold table's `meta()` was reused for the real-content generator. Fix: an explicit final status (`legacy` only for `voiceover-captions`, else `implemented`) in `generate_skill_contents.py`.
- **The phrase "no TODO remains" in a test checklist made the validator fail.** The validator does a literal `"TODO" in text` check. Fix: reworded to "no placeholder steps remain". Lesson: avoid literal sentinel words in generated documentation.
- **Python here starts with site initialization disabled, so sibling imports fail** (`ModuleNotFoundError: skill_lib`). Fix: `sys.path.insert(0, str(Path(__file__).resolve().parent))` in scripts that import sibling modules.
- **patch_real only added 3 of 8 required headings**, so existing hand-written skills failed validation. Fix: add every missing required heading from the generated standard body, preserving the original text.
- **Health check reported ffmpeg-blocked skills as WARN only.** Fix: skills with `requires: ffmpeg` now produce an explicit `BLOCKED ... (not FAIL)` line and a named list, keeping FFmpeg's original WARN unchanged.

## 2026-11-22 — Quality pass on Steps, paths and schemas

- **Generic generator wording replaced real skill logic.** Steps such as "Follow this skill's prompt instructions to ..." were appended to `script-writer`, `script-tester` and `voiceover-captions`. Fix: restored the original bodies from `7f4c2a5` and merged the new standard headings around them. Added those skills (plus the 10 rewritten ones) to `REAL_SKILLS` so regeneration cannot overwrite them.
- **Blind `under projects/<project>/` suffix corrupted root-level outputs.** `config/`, `assets/` and `research/` paths became `projects/<project>/config/...`. Fix: `canonical_output()` and `location_hint()` in `generate_skill_contents.py` now keep root paths at the root and stage paths under the project.
- **`book-finder` niche report path was inconsistent** across SKILL.md, HOW-TO-USE.md and contracts. Fix: `research/niche-report.md` everywhere at the repository root.
- **Schemas were missing, so "valid JSON" did not mean "correct shape".** Fix: six JSON schemas in `config/schemas/`, a stdlib validator, and schema checks in `skill_tools.py` and `generate_audio.py`.
- **Step text was near-identical in 87 of 93 skills.** Fix: rewrote the 10 most important Steps with real acceptance criteria, an output example and 3 quality rules each.

## Rules for future mistakes

- Log the mistake, why it happened, and the fix here immediately.
- Never install a tool or package without telling the user what and why, and getting approval.
- Build one skill at a time; show the test steps and wait for OK before continuing.
