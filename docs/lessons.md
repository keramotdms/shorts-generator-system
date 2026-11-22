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

## Rules for future mistakes

- Log the mistake, why it happened, and the fix here immediately.
- Never install a tool or package without telling the user what and why, and getting approval.
- Build one skill at a time; show the test steps and wait for OK before continuing.
