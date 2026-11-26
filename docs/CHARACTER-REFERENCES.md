# Character Reference Review

Date: 2026-11-26
PC: Office
Purpose: learn what makes a flat vector character look finished, then draw our own
original art. Nothing from these repositories is copied into this project.

## Method

- Three shallow clones (`git clone --depth 1`) went into
  `%TEMP%\opencode\ref-review-2026-11-26`, outside the repository.
- Only file names, counts, licence text, README text and numeric SVG structure were
  measured. No asset was copied, traced or converted.
- The temporary folder was deleted after this review.
- `safety-research/persona_vectors` was intentionally ignored: it is a language-model
  trait dataset, not drawing reference.

## 1. GEE-ME free vector character pack

Repository: <https://github.com/yancymin/GEE-ME-free-vector-character-pack>
Site: <https://geeme.vercel.app/> (JavaScript app, so the repository was inspected)

### Files

| Item | Finding |
| --- | --- |
| Asset folder | `public/people/svg/` and `public/people/png/` |
| Source file | `public/people/GEE-ME-Vector-Character-Pack.sketch` (7,062,541 bytes) |
| Formats | 100 SVG files and 100 PNG files (plus one `.sketch` source) |
| Naming | `gee_me_001.svg` ... `gee_me_100.svg`, matching PNG names |
| Licence file | **None.** No `LICENSE`, `COPYING`, `OFL` or similar file anywhere in the repository |
| Package metadata | `package.json` has `"private": true` and no `license` field |

### README and usage rights

The whole `README.md` is 292 bytes and contains only two image links. It has **no text
about usage, attribution or commercial rights**. There is no licence statement in
`src/` either. The exact README content is:

> `![](https://ph-files.imgix.net/fad58a35-1cda-46dc-bf0f-f294e3f9993c?auto=format&auto=compress&codec=mozjpeg&cs=strip&w=635&h=380&fit=max&dpr=2)`
>
> `![](https://ph-files.imgix.net/e25ea254-1e23-4ce8-871c-05191ab8fd8a?auto=format&auto=compress&codec=mozjpeg&cs=strip&w=635&h=380&fit=max&dpr=2)`

**Commercial use + YouTube monetization clearly allowed? UNCLEAR.**

Reason: the repository publishes no licence and the README grants no rights. A public
GitHub repository without a licence does not grant commercial reuse. The project name
says "free", but a name is not a licence. Do not use these files in a monetized video.

### Measurable style

Measured across the 100 SVGs:

| Property | Measurement |
| --- | --- |
| Canvas | About 556-576 px wide, 1316-1377 px tall |
| Height / width | Median 2.61 (range 1.59-3.26); a tall standing figure |
| Head / total height | Median 0.36 (range 0.28-0.54) across the 58 files with an `id="head"` group; roughly a 1:2.8 head-to-body figure |
| Outline | `stroke-width="1"` on a 556-576 px canvas (about 0.17% of canvas width); Sketch also emitted scaled values such as `1.90140845` and `2` |
| Colours per character | Median 22 distinct hex fills (range 11-49) |
| Shading | Mostly flat fills; gradient mentions median 0, maximum 56 in the most detailed file |
| Layers / groups | Median 12 `<g>` groups (range 6-54) |
| Named groups | `head` (58 files), `upper-limb` (95), `lower-limb` (95), `hand` (40), plus `body`, `Group-N`, `Path`, `Oval` |
| Face, hair, hands | Built as path/ellipse collections inside the head and limb groups; hands are one grouped shape rather than five named finger layers |
| Outfit | Flat path layers inside the body/limb groups, with separate colours rather than texture images |

What makes a GEE-ME character look finished: a very large head, a tall narrow body,
one consistent thin outline, a limited but warm palette, separate named limb groups, and
a few strong dark accents. It is close to a chibi proportion, not a realistic one.

### What we will borrow (principles only)

1. One consistent outline weight for the whole cast.
2. A large head-to-body ratio with a readable silhouette.
3. Named, separate groups for head, hair, hands, outfit and limbs.
4. A small palette with deliberate dark accents, not many random colours.
5. Flat base shapes plus one shadow and one highlight layer, not photographic shading.

## 2. storytold/vectorcraft

1. **What it is:** a large open-source vector illustration application written in Rust,
   with desktop, browser/WASM and headless/MCP modes; about 3,300 files and a Rust
   workspace (`crates/`, `apps/`, `xtask/`).
2. **Licence:** MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`); the
   README badge states the same and third-party notices live in `NOTICE`/`licenses/`.
3. **Does it help our SVG builder?** Not directly. It is a full editor, not a Python
   SVG library, and installing a third-party app is outside this task.
4. **What is reusable:** only concepts such as layer rows, path anchors, live shapes and
   export verification; no code or assets would be copied.
5. **Decision:** reference only; skip. Our builder stays pure Python plus Edge rasterizing.

## 3. mroxso/artcraft-skills

1. **What it is:** 17 agent skills that teach a coding agent to drive the ArtCraft desktop
   suite (VectorCraft, PhotoCraft, FilmCraft, etc.) through a desktop control protocol,
   MCP bridge or headless CLI.
2. **Licence:** MIT (`LICENSE`, copyright 2026 mroxso); bundled upstream reference
   snapshots carry their own MIT licence files.
3. **Does it help our SVG builder?** Not directly. It contains instructions, not drawing
   code or SVG assets, and every skill needs a separately installed application.
4. **What is reusable:** documentation patterns such as command discovery, preview
   verification and save/export checks.
5. **Decision:** reference only; no skill, app or package installed.

## Style target for the "pro" level

The review points to these original, measurable goals:

- Keep the large-head family look (head about 0.30-0.36 of total height).
- Use one outline family at a 1080x1920 render: 14 px outer contour, 10 px outline,
  6 px inner shadow edge and 4 px detail, and never mix unrelated weights inside one
  character.
- Build every character from named layers: hair (4+ strands), head, ears, neck, body,
  outfit, arms, hands (5 fingers), legs, shoes, props.
- Add one shadow layer and one rim-light layer with fixed light from the upper left.
- Add a cloth pattern layer (subtle stripes or weave) so outfits do not read as plastic.
- Keep the palette disciplined: 6+ skin tones, 3-5 outfit colours, 2 accent colours.
- Keep SVG under 200 KB and render under 5 s per character.

No GEE-ME, VectorCraft or ArtCraft file is included in this repository.
