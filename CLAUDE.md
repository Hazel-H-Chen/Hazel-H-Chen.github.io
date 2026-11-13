# Maintaining this site

Notes for whoever edits the site next (Hazel, or Claude in a later session). Plain HTML and CSS, no build step, published by GitHub Pages from `main`. Open `index.html` in a browser to preview; hard-refresh (Ctrl+F5) after changes.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Home page: hero, project list (two groups), skills |
| `projects/*.html` | One page per project; each ends with a "Next:" link |
| `style.css` | All styles. Colour tokens at the top; feature blocks near the end |
| `img/` | Full-size images used on project pages |
| `img/thumbs/` | Resized, trimmed, graded copies used only by the home page list |
| `img/cell-buddy.svg` | Browser-tab icon (the mascot) |
| `projects/thermal-model.js`, `thermal-model-data.js` | Interactive thermal model on the Thermal Model page |
| `SingleCellLumped.m` | The MATLAB model, linked from the Thermal Model page |
| `tools/` | Helper scripts for images and data (see below). Not used by the pages |

Project order on the home page is also the "Next:" chain. Changing the order means editing the `<li>` order in `index.html` **and** the `Next:` links at the bottom of the affected project pages.

## Look and feel: the "cute layer"

Hazel wants the site cutesy/artsy but still readable for recruiters: keep the playful parts at the edges (mascot, frames, handwritten notes) and keep project text and title blocks crisp. The CSS lives in the block headed `cute layer` near the end of `style.css`.

Tokens (in `:root`, with dark-mode values in the `prefers-color-scheme: dark` block):
- `--hand`: Caveat handwriting font (loaded from jsDelivr at the top of `style.css`). Use only for notes and mascot lines, never body text.
- `--peach`, `--mint`, `--lav`, `--butter`: pastel accents. Pills cycle peach, mint, lavender; tape on photos is butter.
- `--hv` / `--hv-text`: the existing high-voltage orange, used for arrows, wavy underlines and the mascot's band.

What is in place:
- **Soft project cards** on the home page (`.index li`): rounded, lift and tilt on hover, tools as `.pill` spans.
- **Wavy underline** on the home section headings (`.group h2`).
- **Rounded corners** on skill cards, the headshot and the interactive model. Project-page title blocks stay square on purpose (they are the "engineering drawing" element).

## The mascot: Cell buddy

A little 18650 cell with a face, blush and an orange band. Hazel chose it; do not use the cat from the HV Indicator silkscreen as a mascot.

- Drawn as inline SVG with `class="buddy"` so it follows light/dark colours. Copy the markup from the `<h1>` on `index.html` or from any page's footer.
- Parts you can style: `.b-line` (outline), `.b-body`, `.b-ink` / `.b-eye`, `.b-band`, `.b-blush`, `.b-wave` (right arm), `.b-spark`.
- Animations: bob (hero only), wave, blink. All switch off under `prefers-reduced-motion`.
- Appears in: next to the name in the hero; every page footer with "thanks for scrolling all the way down!"; the tab icon (`img/cell-buddy.svg`, a simplified copy with its own dark-mode colours).

## Handwritten annotations (the part to expand)

Done so far: the hero photo on `projects/pocketsens.html` and `projects/benchtop-pdb.html`.

Each annotated photo is an inline SVG inside a `<figure class="fig-hero note-fig">`:

```html
<figure class="fig-hero note-fig">
<svg viewBox="0 0 W+360 H+92" role="img" aria-label="(describe the photo AND list what the notes point at)">
  <image class="n-photo" href="../img/PHOTO.jpg" x="180" y="46" width="W" height="H"/>
  <rect class="n-tape" .../>                         <!-- two strips of tape on the top corners -->
  <text class="n-text" x=".." y="..">first line</text>
  <text class="n-text" x=".." y="..">second line</text>
  <text class="n-text n-small" x=".." y="..">(small aside)</text>
  <path class="n-arrow" d="M x y q cx cy dx dy m .. l .. l .."/>   <!-- curve, then the arrowhead -->
</svg>
<figcaption>Caption</figcaption>
</figure>
```

Rules of thumb:
- **Coordinates are the photo's own pixels.** The photo sits at x=180, y=46 at its natural size (W x H), leaving a 180 px margin left and right for notes and 46 px top and bottom. So the viewBox is `0 0 (W+360) (H+92)`. Find a feature's position in the photo, add 180 to x and 46 to y.
- Notes go in the side margins (left notes start near x=0-10, right notes start at about W+200). Lines are 30 px apart; text is 30 px Caveat.
- Arrow: a quadratic curve from beside the note to the feature, then a two-segment arrowhead (`m` back about 15-20 px, `l` to the tip, `l` out again).
- Keep the `aria-label` complete: screen readers do not read the handwritten text separately.
- Notes scale with the photo, so they get small on phones. Prefer short notes (2-3 words a line) and portrait or square photos.
- Check every note against the real board. The current wording was written by Claude from the photos and still needs Hazel's check (see Open items).

Ideas Hazel liked and wants more of:
- Annotate the hero photo on the other project pages (HVC, HV Indicator, Segment BMS, LightCore, Viewfinder, Tractive Battery).
- A handwritten one-liner above each project title on the home cards (for example "fits in a pocket!"). Hazel should write these; do not invent them.
- More small details in the same spirit (mascot cameos, doodles), kept away from the main text.

## Home page thumbnails

The list uses `img/thumbs/*-400.jpg` and a larger copy via `srcset`, never the originals. Pipeline (scripts in `tools/`, run with `powershell -ExecutionPolicy Bypass -File ...`; they use Windows' System.Drawing, no installs needed):

1. `make-thumbs.ps1 -ImgDir <path to img>`: trims white edge strips and writes 400 px and 800 px (or full-width) copies.
2. `pad-plot-thumb.ps1 -Src img/matlab.png -OutDir img/thumbs -Stem thermal_thumb`: the thermal plot is centred on a white 4:3 canvas, not cropped.
3. `grade-thumbs.ps1 -InDir <ungraded thumbs> -OutDir img/thumbs -Names a.jpg,b.jpg`: evens out brightness and contrast. Grade from ungraded copies, not from already-graded files.

Framing is set per thumbnail in `index.html`: `style="object-position: ..."` shifts a crop; class `fit` shows the whole image (used for wide renders and plots) with the page background filling the gaps.

`trim-white-edges.ps1` and `trim-edge-fringe.ps1` remove white strips from full-size images in `img/` (they overwrite in place; run without `-Apply` first to see what they would cut). Images with a genuine white background (Segment BMS render, fuse pack render, tractive battery CAD, lens diagram) are skipped on purpose.

`make-thermal-data.py <folder with the three CSVs> projects/thermal-model-data.js` rebuilds the interactive model's data from the MATLAB inputs.

## Open items (as of 2026-11-13)

- **Thermal model numbers disagree.** The static plots, thumbnail and Results text show a 42.5 C peak; the interactive model shows 46.7 C. MATLAB with `ode45` at `RelTol 1e-4` takes ~0.4 s steps and skips the 0.02 s power spikes; adding `'MaxStep', 0.02` (or `RelTol 1e-9`) gives 46.7-46.9 C and about 10% charge left. Re-run MATLAB, re-export the plots and update the text.
- **Lapsim data is public** via `projects/thermal-model-data.js`. Confirm the team is fine with that before pushing.
- **60 C rules limit** line in the interactive plot is from memory; check the current FSAE rulebook.
- `SingleCellLumped.m` still contains a thumbnail-export snippet that exports the SOC figure; tidy it since the page links to the file.
- **Missing images** on `projects/segment-bms.html`: `img/assembled-stack.jpg` and `img/mounted-on-segment.jpg` do not exist.
- **Unchecked wording** written by Claude: the PocketSens and Benchtop PDB annotations, and on the Fusible Link page the list of boundary conditions, the sensitivity claim, "holds whatever the boundary conditions are", and the parallel-group paragraph.
- **Low-resolution photos** that look soft: viewfinder finished (312 px), viewfinder photo (434), LightCore PCB (562), PDB assembled (588), PocketSens PCB (602), LightCore assembled (655). Originals from the camera roll would fix them.
- **Thumbnail ideas not done:** lit-up/powered-on shots (HV Indicator, LightCore, PocketSens), Segment BMS swapped to the chip close-up, fusible link cropped to just the link, thermal thumbnail redrawn in site colours.
- `img/MatlabThermalPlot.png` is no longer used anywhere.
- Nothing from the 2026-11-12/13 session has been committed or pushed yet.
