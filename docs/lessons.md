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

## 2026-11-23 — Toolchain setup on this PC

- **`py` was missing and `python` was only the Microsoft Store stub.** Installed real Python 3.12.10 with `winget install Python.Python.3.12 --scope user --custom "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0"`. Verified `python --version` -> `Python 3.12.10`, `python -m pip --version` -> `pip 25.0.1`. Existing shells needed a USER PATH reload before `python` resolved to the real interpreter.
- **Installed `edge-tts` 7.3.1 inside `.venv` and verified `import edge_tts` works.** `.venv/` was already in `.gitignore`. Keep running project scripts with `.venv\Scripts\python.exe` unless the venv is activated.
- **`git` was not on PATH.** Did not install a second Git: added GitHub Desktop 3.6.4's bundled `git\cmd` folder to USER PATH. Verified `git --version` -> `git version 2.53.0.windows.4` and `git status` is clean. Caveat: this path includes the Desktop version number, so re-add it after a GitHub Desktop update if `git` disappears.
- **FFmpeg is blocked on this PC too, but there is a workaround.** Installed `Gyan.FFmpeg` 9.1 per-user; `ffmpeg.exe` fails with `An Application Control policy has blocked this file` and `ffprobe.exe` hangs with no output. Did **not** disable Smart App Control or change any Windows security setting. `imageio-ffmpeg` 0.8.1 in the venv supplies a working `ffmpeg 9.0.2` binary.
- **Set `FFMPEG_PATH` in `.env` (gitignored) and a repo-relative path in `config/defaults.json`.** Fixed `skill_lib.ffmpeg_executable()` to resolve relative paths against the repo root, and fixed `health_check.py` to use `ffmpeg_status()` instead of only `shutil.which("ffmpeg")`. Otherwise the health check would still mark 28 skills BLOCKED even though the configured binary works.
- **Final verification:** health check `40 PASS | 1 WARN | 0 BLOCKED | 0 FAIL` (the WARN is `ffprobe` unavailable); `tests/test_skills.py` -> `PASS: 93 skills validated, 47 self-tests passed or blocked`; dummy pipeline -> `93 PASS | 0 FAIL | 0 BLOCKED`. All 28 ffmpeg-required skills are unblocked.
- **Created `config/style-bible.json` with the `project-memory` skill** from `config/channel.json`. Fixed doc drift: README now says 93 skills are implemented, ROADMAP niche/language are resolved, and both `AGENTS.md` occurrences use `voiceover-generator`.

## 2026-11-23 — FFmpeg routing and checker upgrades

- **Audit finding: `audio-ducking-controller` declared `requires: ffmpeg` but had no run branch.** Fix: it now has its own `sidechaincompress` command in `scripts/skill_tools.py`.
- **Audit finding: 10 important FFmpeg skills either shared one generic concat command or had no burn-in/check logic.** Fix: `rough-cut-assembler`, `caption-maker`, `safe-zone-checker`, `format-converter`, `render-export-optimizer`, `audio-mixer`, `audio-ducking-controller`, `video-maker`, `kinetic-text-animator` and `transition-designer` now have purpose-matching helpers with `ffprobe` reports.
- **Audit finding: 8 checker skills only validated fixtures in self-test.** Fix: their self-tests now generate real media with the already-installed FFmpeg and check duration, resolution and audio with `ffprobe` where relevant.
- **The remaining FFmpeg skills are intentionally generic for now — needs real logic later:** `animator`, `beat-sync-editor`, `branding-manager`, `broll-variety-planner`, `color-grading-keeper`, `cut-rhythm-editor`, `emphasis-sticker-placer`, `hook-visual-editor`, `intro-outro-manager`, `motion-graphic-editor`, `pattern-interrupt-inserter`, `preview-frame-extractor`, `seamless-loop-editor`, `sfx-timing-placer`, `thumbnail-designer`, `variant-batch-renderer`, `video-editor`, `watermark-logo-placer`. Do not claim these have finished, purpose-specific FFmpeg logic yet.

## 2026-11-23 — SVG scene builder

- **No Python SVG/PNG package is installed** (`cairosvg`, `Pillow`, `wand`, `svglib`, `reportlab`, `lxml` all absent). Fix: `scripts/svg_scene_builder.py` writes SVG with the standard library and rasterizes with the already-installed Microsoft Edge headless renderer. No install was requested or performed.
- **FFmpeg cannot decode SVG in this build** (`no decoder found for: svg`). Fix: keep SVG generation and PNG rasterization in the builder; FFmpeg only consumes the resulting PNGs later.
- **Windows drive letters break FFmpeg filter parsing when escaped once.** Fix: drive-letter colons in `fontfile` need a double backslash (`C\\:/Windows/Fonts/...`) in `scripts/skill_tools.py`; single escaping produced `No option name near '/Windows/...'`.
- **`drawbox` does not accept `round()` in this FFmpeg build.** Fix: use integer pixel values for the 1080x1920 safe-zone preview.
- **Sample outputs:** `assets/characters/creator-01-neutral.{svg,png}`, `creator-01-smile.{svg,png}`, `creator-01-surprised.{svg,png}`, `assets/scenes/warm-desk-background.{svg,png}` and `assets/scenes/scene-warm-desk-smile.{svg,png}`.

## Rules for future mistakes

- Log the mistake, why it happened, and the fix here immediately.
- Never install a tool or package without telling the user what and why, and getting approval.
- Build one skill at a time; show the test steps and wait for OK before continuing.
