# hazel-h-chen.github.io

My engineering portfolio. Plain HTML and CSS, no build step.

## Put it online (one time, ~10 minutes)

1. On GitHub, create a **new public repository** named exactly
   `Hazel-H-Chen.github.io` (GitHub treats this name as your personal site).
2. On the empty repo page, click **uploading an existing file**, then drag in
   everything from this folder: `index.html`, `style.css`, `README.md`, and the
   `img`, `fonts`, and `projects` folders. Commit.
3. Go to **Settings > Pages**. Under "Build and deployment", set Source to
   **Deploy from a branch**, branch **main**, folder **/ (root)**. Save.
4. Wait a minute or two, then open **https://hazel-h-chen.github.io**.

Every time you upload or commit a change, the site updates within a minute or two.

## Before you share the link

- [ ] Replace `img/headshot.jpg` with your photo (square crop, same filename).
- [ ] Add your resume as `resume.pdf` in the top folder. The Resume links point there.
- [ ] Read the HVC page carefully (see the notes I sent you).
- [ ] Add HVC images (see below).

## Editing

- **Text:** open the page in any text editor (VS Code is easiest) and edit the
  words between the tags. Each project is one file in `projects/`.
- **Colors:** all colors are at the top of `style.css` under `:root`. Dark mode
  colors are right below.
- **Adding an image:** put the file in `img/`, then paste this where you want it:

  ```html
  <figure><img src="../img/your_file.jpg" alt="What it shows"><figcaption>What it shows</figcaption></figure>
  ```

  Add `class="fig-hero"` to the `<figure>` to make it the big image at the top
  of a page. Wrap two figures in `<div class="fig-row"> ... </div>` to put them
  side by side.

- **HVC images:** in `projects/hvc.html`, look for the comment that says
  `ADD IMAGES HERE`. Replace that whole comment with a hero figure like the one
  above. Good candidates: a 3D render, the bench test setup, a scope capture
  of precharge.

- **Adding a project:** copy an existing page in `projects/`, rename it, edit
  it, then copy one `<li>...</li>` block in `index.html` and point it at the
  new page.

## Preview locally

Double-click `index.html` to open it in your browser. Everything works offline.

Fonts: Barlow and Barlow Condensed, self-hosted in `fonts/` under the SIL Open Font License.
