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
- **The remaining FFmpeg skills were intentionally generic at this point:** `animator`, `beat-sync-editor`, `branding-manager`, `broll-variety-planner`, `color-grading-keeper`, `cut-rhythm-editor`, `emphasis-sticker-placer`, `hook-visual-editor`, `intro-outro-manager`, `motion-graphic-editor`, `pattern-interrupt-inserter`, `preview-frame-extractor`, `seamless-loop-editor`, `sfx-timing-placer`, `thumbnail-designer`, `variant-batch-renderer`, `video-editor`, `watermark-logo-placer`. **SUPERSEDED later on 2026-11-23** by `scripts/effect_ffmpeg.py`: all 18 now have purpose-specific commands and ffprobe self-tests.

## 2026-11-23 — SVG scene builder

- **No Python SVG/PNG package is installed** (`cairosvg`, `Pillow`, `wand`, `svglib`, `reportlab`, `lxml` all absent). Fix: `scripts/svg_scene_builder.py` writes SVG with the standard library and rasterizes with the already-installed Microsoft Edge headless renderer. No install was requested or performed.
- **FFmpeg cannot decode SVG in this build** (`no decoder found for: svg`). Fix: keep SVG generation and PNG rasterization in the builder; FFmpeg only consumes the resulting PNGs later.
- **Windows drive letters break FFmpeg filter parsing when escaped once.** Fix: drive-letter colons in `fontfile` need a double backslash (`C\\:/Windows/Fonts/...`) in `scripts/skill_tools.py`; single escaping produced `No option name near '/Windows/...'`.
- **`drawbox` does not accept `round()` in this FFmpeg build.** Fix: use integer pixel values for the 1080x1920 safe-zone preview.
- **Sample outputs:** `assets/characters/creator-01-neutral.{svg,png}`, `creator-01-smile.{svg,png}`, `creator-01-surprised.{svg,png}`, `assets/scenes/warm-desk-background.{svg,png}` and `assets/scenes/scene-warm-desk-smile.{svg,png}`.

## 2026-11-23 — 55 TEMPLATE skills rewritten to REAL

- **Read-only baseline first:** 38 REAL / 55 TEMPLATE. No TEMPLATE skill was on the strict first-video chain. The 55 targets were listed explicitly in `tests/test_no_template.py` so the anti-fake test reports exactly 55 failures before the rewrite and 0 afterwards.
- **The first version of the anti-fake test checked all 92 implemented skills** and reported 92 failures because the 38 already-REAL skills lack the new example heading. Fix: scope the regression guard to the 55 audited targets; keep the strict new content requirements there. Lesson: a baseline guard must match the audited scope, not every file in the folder.
- **Formatting bug in the rewrite renderer:** input items already started with `- `, so the renderer produced `- - path`. Fix: append the item unchanged when it already has a bullet.
- **`effect_ffmpeg.py` referenced two builder functions before they were defined.** Python resolved names at call time, so the module imported fine but the self-test crashed with `NameError`. Fix: move `build_broll_variety` and `build_cut_rhythm` above the `BUILDERS` map.
- **`drawbox` colour must be `0xRRGGBB`, not the CSS `#RRGGBB` from `style-bible.json`.** Fix: `ffmpeg_color()` strips `#` and prepends `0x`. Lesson: config colours are not FFmpeg colours.
- **`drawtext` does not accept `ih-154` in this FFmpeg build** (`Undefined constant or missing '(' in 'ih-154'`), and `drawbox` needs `iw`/`ih`. Fix: use `main_w`/`main_h` for drawtext expressions and `iw`/`ih` for drawbox geometry.
- **`cut-rhythm-editor` self-test failed because its concat command intentionally drops audio** while the generic check expected audio. Fix: added it to `NO_AUDIO_SKILLS` in `scripts/effect_ffmpeg.py`.
- **Input bullets, unique Steps and examples matter more than prose length.** Each of the 55 skills now has its own When to use, criteria with numbers, a filled example that validates against a schema, 3 quality rules, unique Steps, and Failure handling. Duplicate Step signatures are caught by the anti-fake test.
- **No API access and no fake data:** 7 growth skills are marked `api_needed: later` and read manual exports from `projects/<project>/10-publish/inputs/`: `ab-tester`, `analytics-feedback-loop`, `comment-community-manager`, `monetization-tracker`, `scheduler-publisher`, `youtube-analyst`, `youtube-seo-specialist`. Four more skills need manual notes instead of APIs: `script-user-tester` (viewer feedback), `competitor-analyzer` (competitor notes), `fact-checker` (source notes), `seo-specialist` (keyword notes). They stop or WARN when the export is missing rather than inventing rows.
- **Asset-dependent skills degrade safely:** music/SFX, stock assets, logos and character layers must already exist locally; when they do not, the skill writes WARN instead of downloading anything.
- **`scripts/audit_skill_status.py` initially flagged `orchestrator` as TEMPLATE** because its Steps use `scripts/orchestrator.py`, not a `projects/<project>/` path. Fix: accept `scripts/` as a concrete path hint. Lesson: audit criteria must fit core tooling as well as content skills.
- **`scenario-designer` still had one leftover generic Step** even though it was already counted REAL. Fix: replaced it with a concrete flat-shape layout instruction. Lesson: run a repo-wide grep for the generic phrase, not only a scoped test.
- **Verification after each batch:** `scripts/health_check.py`, `tests/test_skills.py`, `tests/smoke/run_dummy_pipeline.py` and `tests/test_no_template.py` all passed after A (40 failures left), B (32), C (13) and D (0). Final full audit: `93 REAL / 0 TEMPLATE`.
- **No installs, no `.env` edits, no Windows setting changes, no force push, no token in chat or repo.** Push uses Git Credential Manager; if it fails, tell the user to sign in with GitHub Desktop or `gh auth login`.

## Rules for future mistakes

- Log the mistake, why it happened, and the fix here immediately.
- Never install a tool or package without telling the user what and why, and getting approval.
- Build one skill at a time; show the test steps and wait for OK before continuing.

## 2026-11-23 — Four-phase review fix

- **A green test suite can hide a broken chain.** `tests/test_skills.py` and the smoke test passed while `caption-maker` never wrote `07-edit/captions.json`, no skill produced `08-final-test/final-video.mp4`, and `handover` required its own output as an input. Lesson: always run an end-to-end dry run with fake data, not only unit-style harnesses.
- **A handover report must be an output, never an input.** Fixed the circular dependency and made `handover` exit non-zero when any of its three real upstream assets is missing. Lesson: `ready: false` with exit 0 is a silent failure.
- **The canonical final video needs one declared producer.** `render-export-optimizer` is now the only skill that writes `projects/<project>/08-final-test/final-video.mp4`; every consumer reads that exact path. Lesson: multiple possible final files make downstream checks meaningless.
- **`contract_output()` must select by filename, not just stage.** Without that, a JSON report could overwrite a media deliverable. Lesson: when a skill emits several file types, resolve the declared output by its basename.
- **Exact contract paths need a graph test.** Replacing ~68 descriptive Input/Output strings fixed readability, but only `tests/test_chain.py` proves every input is produced earlier and no output is duplicated. Lesson: path strings are data; validate them as a dependency graph.
- **A passing self-test that only prints `PASS` proves nothing.** Six skills printed a fixed string and ten only checked whether FFmpeg was available. Lesson: every self-test must assert a real expected value — schema validity, round-tripped JSON, or ffprobe-measured duration/resolution — and the harness must count PASS/BLOCKED honestly.
- **Anti-template tests can miss copy-paste among already-real skills.** The 55 rewritten skills had unique Steps, but 99 pairs among the original 38 were over 80% identical after removing the skill name. Lesson: run pairwise similarity across all skills, not only the ones previously flagged as templates.
- **Legitimate Bangla text is not hardcoding.** Bangla rules, ৳ amounts and filled config examples may contain niche/language literals; the real test is whether values load through project-memory. Lesson: do not “fix” valid localisation examples just to make a grep quiet.
- **Analyzer regexes can swallow adjacent fenced blocks.** A bare closing ``` before a ```json block was parsed as the opening fence, hiding a valid example. Lesson: use one JSON fence per section or avoid mixing markdown and JSON fences when a regex extracts examples.
- **Recompute final verdicts from current files.** The first final checker still used static issue sets from the original audit and reported stale failures after the fixes. Lesson: after each phase, regenerate facts and derive verdicts from live files and tests.
- **Changing a shared output path breaks downstream contracts silently.** Moving `trend-report.json` to `research/trend-cache/` left `story-thinker` and `content-calendar` pointing at the old project path. `tests/test_chain.py` caught it. Lesson: update every consumer, its SKILL.md and the chain regression check in the same commit.
- **Optional APIs need an explicit unavailable state.** `trend-finder` reports `unavailable`/`warn` per source and writes an empty `trends` list instead of inventing rows when a key or package is missing. Lesson: a missing source is data the report must carry, not a reason to fabricate a trend.

## 2026-11-23 — Parametric character designer

- **Keep one renderer for scenes and previews.** `svg_scene_builder.character_markup()` now delegates to `scripts/character_designer.py` when a character has `parts`; the legacy flat-shape path still works for older files. Lesson: extend the shared renderer instead of adding a second one.
- **A locked character is a data file, not a drawing.** The winner stores every part ID, colour and proportion in `assets/characters/creator-01/character.json`; two renders are compared by SHA-256 to prove consistency. Lesson: consistency is checkable only when the design is structured data.
- **No Python package was installed for SVG or PNG.** The parts library is JSON with `{skin}`, `{hair}`, `{outfit}`, `{accent}`, `{outline}`, `{light}`, `{eye}` placeholders, resolved with `str.replace` and rasterized by the existing Edge renderer. Lesson: templates plus the standard library are enough for deterministic flat-shape art.
- **Picking by rule beats picking at random.** Role, age, personality and niche map to documented part choices, and `fit_score` ranks the three candidates. Lesson: a documented rule is reproducible and explainable to the viewer.
- **Migrate the contract and every consumer together.** Moving the canonical file to `assets/characters/creator-01/character.json` required updating `config/skill-contracts.json`, ten SKILL.md files, `tests/test_chain.py`, docs and the regeneration scripts in one pass. The three legacy expression views are regenerated from the locked design so older consumers stay valid. Lesson: a new canonical path is a graph change, not a single find-and-replace.

## 2026-11-24 — Home PC production checks (ffprobe, pytrends, Bangla)

- **`ffprobe` from the winget `Gyan.FFmpeg` 9.1 build runs even though `ffmpeg.exe` is blocked.** Earlier notes said it hung; it works when called by absolute path. Fix: `FFPROBE_PATH` in `.env`, `ffprobe_path` in `config/defaults.json`, and `skill_lib.ffprobe_executable()` / `ffprobe_status()` so scripts and the health check stop guessing a sibling `ffprobe.exe` next to the imageio-ffmpeg binary. Lesson: blocked `ffmpeg.exe` does not automatically mean blocked `ffprobe.exe`; test the exact binary by absolute path.
- **Environment variables inside config paths need expansion.** `%LOCALAPPDATA%` in `config/defaults.json` is expanded with `os.path.expandvars` before the existence check. Lesson: a config path is not a filesystem path until variables are expanded.
- **The `edge-tts.exe` launcher is blocked by Application Control, but the package is not.** `python -m edge_tts` works, and `scripts/generate_audio.py` already calls the Python API. Lesson: when a console-script shim is blocked, call the module through the interpreter instead of changing Windows security.
- **Bangla rendering is correct with the current FFmpeg.** The imageio-ffmpeg 9.0.2 build has `libass`, `libfreetype`, `libfribidi` and `libharfbuzz` (no `libraqm`). A 3-second ASS caption test rendered "টাকা বাঁচানোর সহজ উপায়" with intact conjuncts and vowel signs, so the Edge PNG fallback is not needed. libass prints `Error opening memory font 'OFL.txt'` because `fontsdir` contains the license text file; it is harmless.
- **Keep Bangla fonts inside the repo.** Downloaded Noto Sans Bengali and Hind Siliguri (OFL) into `assets/fonts/<family>/` with `OFL.txt` next to each. `font_file()` now searches nested folders and caption burn-in passes `fontsdir`. No Windows font install was needed.
- **`pytrends` 4.9.2 installed in `.venv` only** and then listed in `requirements.txt`. `YOUTUBE_API_KEY` is still not set; the name stays in `.env.example` and the value belongs only in `.env`.
- **PC-aware health check:** `PC_ROLE=home|office` is read from the environment or `.env`. On `office`, a missing `edge-tts`, `pytrends` or Bangla font reports `INFO`; on `home` it reports `WARN`. The summary now counts INFO separately so informational lines never look like failures.
- **`project-memory` must not erase font paths.** Re-running it rebuilt `style-bible.json` from a template and dropped `font_path`, licenses and fallback fonts. Fix: preserve those keys from the existing style bible. Lesson: a generated config must merge recorded choices, not blindly overwrite them.
- **Edge headless SVG → PNG PASS** and Bangla TTS PASS with `bn-BD-PradeepNeural` (3.408 s sample). No installs beyond the approved `pytrends`, no Windows security changes, no secrets printed.

## 2026-11-24 - Output format registry

- **One format profile per output, not per extension.** `config/output-formats.json` defines 13 named profiles; every declared output in `config/skill-contracts.json` points to exactly one. A single `.mp4` can be a clip or a final video, so the profile carries the checkable parameters (codec, profile, fps, faststart, duration), not just the suffix. Lesson: declare the contract in data, then validate the data before validating files.
- **A format change touches three places at once.** Each of the 113 outputs needed a `format` field in the contract, a matching line in its SKILL.md Output section, and a row in `docs/OUTPUT-FORMATS.md`. `tests/test_formats.py` checks all three so they cannot drift. Lesson: generate the repetitive edits from one source of truth and let a regression test prove consistency.
- **ffprobe is optional on office PCs.** `scripts/format_validator.py` reports a missing ffprobe as INFO when `PC_ROLE=office` and FAIL on `home`. The role is read from the environment or the single `PC_ROLE=` line in `.env`; no other dotenv value is loaded. Lesson: media checks must degrade to INFO where production tooling is deliberately absent.
- **FFmpeg filtergraph paths must use forward slashes.** After the Home PC font commit, `font_file()` returned a repo-relative Windows path with backslashes; `fontfile=assets\fonts\...` was mangled by FFmpeg's escape parser and fell back to fontconfig, so three drawtext self-tests failed with `Fontconfig error: Cannot load default config file`. Fix: `Path(lib.relative(font)).as_posix()` in `effect_ffmpeg.font_part()`, matching `cmd_kinetic_text`. Lesson: convert Windows paths to POSIX form before putting them inside an FFmpeg filter string.

## 2026-11-26 - Pro character detail and cast

- **uild_design() appends a candidate suffix to every id.** Reusing it for cast members produced mentor-01-candidate-03 folders, so the cast report looked for mentor-01 and crashed. Fix: reset id to the cast id after building the design. Lesson: a builder that names candidates must not be trusted to name final deliverables.
- **Not every layer varies by expression.** im_light, inner_shadow, ear_shading and 
eck_shading are static pro layers, so an assertion that every named layer changes per expression failed. Lesson: assert expression variation only on expression layers, and separately assert the static shading layers exist.
- **A detail level is additive, not a repaint.** Moving creator-01 from ich to pro re-ran the old brief through preserve_creator_identity() and kept role, palette, outfit and proportions byte-identical while the layer count rose from 31 to 40. Lesson: compare the locked identity fields in the self-test before trusting a "new look".
- **The visible difference between rich and pro is subtle by design.** Outline variation, rim light, ear/neck shading, weave and extra hair strands read at full size but almost vanish in a thumbnail. Lesson: keep a side-by-side compare-rich-pro.png so the reviewer can judge the change without opening the SVG.
## 2026-11-28 - scenery-designer background plates

- **A filter on a layer group costs 4x more than a filter per element.** The first plate put `feGaussianBlur` on `id="bg-bokeh"`; because the four lights span almost the whole canvas, Edge rasterised a 1080x1920 blur and a render took 5.9s. Moving the filter onto each light (region `-40%/180%`) dropped it to ~4.0s with no visible change. Lesson: scope an SVG filter to the element bbox, not to the layer that happens to contain it.
- **Measure a timing floor before copying someone else's budget.** `character-designer` allows 5s per PNG render, so `scenery-designer` started there. A bare one-rectangle Edge screenshot on this machine already costs 2.9-3.7s and desktop noise pushed single plate renders as high as 6.5s; a warm plate render hit 4.95s of 5s. Fix: `MAX_RENDER_SECONDS = 8.0` with the measurement written into the comment above it, and the self-test times the second (warm) render instead of the first. Lesson: a copied limit is a guess until you measure the baseline it has to sit on top of.
- **Timing the first render measures start-up, not the file.** character-designer renders twice before its timed render; repeating that order here made the number stable. Lesson: warm the engine in an untimed pass, then measure.
- **Colour discipline needs an enforced choke point, not a review.** `blend()` refuses any input that is not a style-bible colour or an earlier blend result, so a hardcoded hex raises `SkillError` before anything is rendered; the self-test then re-scans every `fill`/`stop-color`/`stroke` in the finished SVG. Lesson: make the only path to a colour go through a function that validates, and assert on the output too.
- **Keyword order decides the scene-to-plate map.** "night city" would have matched bedroom-night because `night` is a mood word. Location words are matched first (classroom, shop-interior, street-night, ceremony-hall) and mood words last. Lesson: when several rules can match the same text, order them from most specific to least specific and test the ambiguous case.
- **A new skill touches the skill-count in seven places.** `skill_tools` (contract count), `audit_skill_status` (REAL count and both messages), `README`, `docs/SKILL-INDEX`, `docs/HOW-TO-USE`, `pipeline-health-checker/SKILL.md` and `run_dummy_pipeline.py`. Lesson: a hardcoded total is a distributed constant; grep for it before committing.
