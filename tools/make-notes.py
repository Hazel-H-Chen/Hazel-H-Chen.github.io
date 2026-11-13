"""Builds the handwritten photo annotations and writes them into the project pages.

Run from anywhere:   python tools/make-notes.py
Add --preview DIR to also write one small test page per figure into DIR
(used for checking placement with a headless-Chrome screenshot).

Each entry in FIGS describes one annotated photo:
  page      project page in projects/
  img       file in img/ (the script finds the <figure> line that uses it)
  size      the image's real pixel size (w, h)
  width     how wide to draw the photo inside the SVG, in SVG units.
            Text is always 30 units tall, so ~600 keeps notes readable.
  margins   (left, top, right, bottom) blank space around the photo for notes.
            Side notes: (180, 46, 180, 46). Wide images: small sides, tall top/bottom.
  caption   the figcaption
  label     aria-label: describe the photo AND what the notes point at
  notes     list of dicts:
              at     (x, y) of the first text line, in SVG units (whole canvas)
              lines  text lines, 30 units apart
              small  optional smaller grey aside under the lines
              anchor optional 'middle' or 'end'
              arrow  optional (start, target, bend): start is (x, y) in SVG units,
                     target is ('p', x, y) in the PHOTO's own pixels or (x, y) in
                     SVG units, bend is how far the curve bows sideways (+/-).

The PocketSens and Benchtop PDB annotations were written by hand before this
script existed and are not managed here.
"""
import html
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIDE = (180, 46, 180, 46)

FIGS = [
    dict(
        page="hvc.html", img="hvc_prototype.jpg", size=(1400, 1326), width=620, margins=SIDE,
        caption="HVC prototype",
        label="Assembled HVC prototype board, with handwritten labels: isolated DC-DC modules, "
              "the designers' names on the silkscreen, the Teensy 4.1 header, the precharge relay, "
              "and the two isoSPI transformers",
        notes=[
            dict(at=(8, 100), lines=["isolated", "DC-DCs"], arrow=((96, 108), ("p", 425, 175), -30)),
            dict(at=(8, 372), lines=["we signed", "it :)"], arrow=((108, 380), ("p", 395, 775), -34)),
            dict(at=(4, 520), lines=["Teensy 4.1", "plugs in here"], arrow=((140, 548), ("p", 480, 1150), 30)),
            dict(at=(820, 250), lines=["precharge", "relay"], arrow=((814, 262), ("p", 1030, 590), 26)),
            dict(at=(820, 420), lines=["isoSPI", "transformers"], small="(two = a ring)",
                 arrow=((814, 430), ("p", 1065, 830), -22)),
        ],
    ),
    dict(
        page="hv-indicator.html", img="hvi_v1_flyback.jpg", size=(1400, 1284), width=620,
        margins=(180, 46, 180, 78),
        caption="V1 board with my flyback board wired in place of the Murata module",
        label="Voltage Indicator V1 board wired to a separate isolated flyback board, with handwritten "
              "labels: the flyback board, the empty footprint where the Murata module sat, the "
              "high-voltage input, the VIPer06 buck stage, and the isolated 12 V output",
        notes=[
            dict(at=(8, 130), lines=["my flyback", "board"], small="(LM25180)",
                 arrow=((92, 196), ("p", 90, 440), 26)),
            dict(at=(820, 150), lines=["tractive", "bus in"], small="(HV!)",
                 arrow=((814, 150), ("p", 840, 440), 60)),
            dict(at=(820, 350), lines=["VIPer06", "buck stage"], arrow=((814, 362), ("p", 1215, 715), 20)),
            dict(at=(186, 672), lines=["Murata module sat here"], arrow=((330, 646), ("p", 700, 760), -50)),
            dict(at=(600, 672), lines=["isolated 12 V out"], arrow=((640, 646), ("p", 760, 1040), -24)),
        ],
    ),
    dict(
        page="segment-bms.html", img="Segment_MB_3drender.png", size=(1660, 672), width=900,
        margins=(30, 84, 30, 84),
        caption="Rev 2 main board in Altium",
        label="3D render of the Rev 2 BMS main board, with handwritten labels: an isoSPI port at each "
              "end, the ADBMS6830 cell monitor in the centre, the balance resistors, and the FPC "
              "connector to the cell tap board",
        notes=[
            dict(at=(40, 44), lines=["isoSPI port"], arrow=((150, 54), ("p", 200, 40), 14)),
            dict(at=(480, 44), anchor="middle", lines=["ADBMS6830: reads all 16 cells"],
                 arrow=((492, 58), ("p", 835, 250), -22)),
            dict(at=(920, 44), anchor="end", lines=["...and another"], arrow=((850, 54), ("p", 1470, 40), -14)),
            dict(at=(40, 508), lines=["balance resistors"], small=None,
                 arrow=((200, 482), ("p", 330, 610), 14)),
            dict(at=(920, 508), anchor="end", lines=["FPC to the cell tap board"],
                 arrow=((800, 482), ("p", 1400, 440), 30)),
        ],
    ),
    dict(
        page="segment-bms.html", img="SegmentDB_redner.png", size=(912, 961), width=570, margins=SIDE,
        caption="Rev 2 cell tap daughterboard",
        label="3D render of the Rev 2 cell tap daughterboard, with handwritten labels: thermistors, "
              "the pads the cell tabs clamp to, the FPC connector footprint, the per-tap fuses, and "
              "a note that the board is now 2 layers instead of 6",
        notes=[
            dict(at=(8, 200), lines=["thermistors"], arrow=((140, 196), ("p", 345, 318), -24)),
            dict(at=(8, 440), lines=["cell tabs", "clamp here"], arrow=((118, 440), ("p", 205, 585), -22)),
            dict(at=(770, 110), lines=["FPC lands", "here"], arrow=((764, 118), ("p", 655, 170), 22)),
            dict(at=(770, 380), lines=["a fuse on", "every tap"], arrow=((764, 392), ("p", 560, 590), -26)),
            dict(at=(770, 580), lines=["only 2 layers"], small="(was 6!)"),
        ],
    ),
    dict(
        page="lightcore.html", img="lightcore_assembled.jpg", size=(655, 655), width=620, margins=SIDE,
        caption="Assembled V1.2 LightCore",
        label="Assembled V1.2 LightCore, with handwritten labels: the encoder knob, the opening the "
              "light comes out of, the aluminum side walls, and the switches",
        notes=[
            dict(at=(8, 400), lines=["encoder", "knob"], arrow=((92, 408), ("p", 146, 376), -30)),
            dict(at=(820, 130), lines=["light comes", "out here"], arrow=((814, 140), ("p", 368, 204), 50)),
            dict(at=(820, 290), lines=["aluminum", "side walls"], arrow=((814, 300), ("p", 548, 268), 16)),
            dict(at=(820, 440), lines=["switches"], arrow=((814, 432), ("p", 500, 364), -20)),
        ],
    ),
    dict(
        page="hybrid-viewfinder.html", img="viewfinder_photo.jpg", size=(434, 581), width=434, margins=SIDE,
        caption="Viewfinder prototype",
        label="Viewfinder prototype, with handwritten labels: the rear lens, the beam splitter hidden "
              "inside the body, and the front lens that was CNC machined and polished",
        notes=[
            dict(at=(8, 110), lines=["rear lens"], arrow=((104, 104), ("p", 26, 120), -18)),
            dict(at=(8, 300), lines=["beam splitter", "hides inside"], arrow=((150, 300), ("p", 125, 210), -24)),
            dict(at=(634, 180), lines=["lens I CNC'd", "+ polished"], arrow=((628, 196), ("p", 345, 235), 24)),
        ],
    ),
    dict(
        page="tractive-battery.html", img="tb_enclosure_fab.jpg", size=(1400, 1189), width=620, margins=SIDE,
        caption="Pack enclosure during fabrication",
        label="Partly built aluminum pack enclosure, with handwritten labels: the "
              "internal dividers, and the perforated floor vents",
        notes=[
            dict(at=(8, 400), lines=["internal", "dividers"], arrow=((104, 406), ("p", 530, 690), -40)),
            dict(at=(820, 500), lines=["floor vents"], arrow=((814, 492), ("p", 870, 885), -20)),
        ],
    ),
    dict(
        page="tractive-battery.html", img="tb_module_assembly.jpg", size=(1143, 1400), width=500, margins=SIDE,
        caption="Module during assembly, before the cell tabs are connected",
        label="Module during assembly, with handwritten labels: the 16 pouch cells, "
              "the cell tabs not yet bolted together, and the foam and heat spreader between cells",
        notes=[
            dict(at=(8, 440), lines=["16 pouch", "cells"], arrow=((100, 446), ("p", 172, 900), -20)),
            dict(at=(700, 200), lines=["tabs, not", "bolted yet"], arrow=((694, 214), ("p", 700, 540), 30)),
            dict(at=(700, 460), lines=["foam + heat", "spreader in", "every gap"],
                 arrow=((694, 480), ("p", 655, 980), -24)),
        ],
    ),
    dict(
        page="bms-hand-soldering.html", img="bms_adbms6830_closeup.jpg", size=(1400, 1063), width=620,
        margins=SIDE,
        caption="Hand-soldered passives and ADBMS6830 leads under the microscope",
        label="Microscope view of hand-soldered capacitors next to the drag-soldered ADBMS6830 leads, "
              "with handwritten labels: 0402 capacitors soldered one at a time, the ADBMS6830, and "
              "its drag-soldered leads",
        notes=[
            dict(at=(4, 190), lines=["0402 caps,", "one at a time"], small="(1 mm long!)",
                 arrow=((150, 200), ("p", 425, 405), -26)),
            dict(at=(820, 110), lines=["ADBMS6830"], arrow=((860, 122), ("p", 1290, 330), -24)),
            dict(at=(820, 340), lines=["drag-soldered", "leads"], arrow=((814, 350), ("p", 1040, 600), -22)),
        ],
    ),
    dict(
        page="fusible-link-simulation.html", img="fuse_pack_render.jpg", size=(633, 445), width=620,
        margins=SIDE,
        caption="Fusible link layout in a custom cylindrical-cell pack",
        label="Render of a cylindrical-cell pack joined by a nickel strip, with handwritten labels: "
              "the nickel strip, and the narrow necks that act as the fuses, one per cell",
        notes=[
            dict(at=(8, 90), lines=["nickel strip"], arrow=((126, 82), ("p", 92, 42), -18)),
            dict(at=(820, 250), lines=["skinny necks", "= the fuses"], small="(one per cell)",
                 arrow=((814, 244), ("p", 502, 166), 22)),
        ],
    ),
    dict(
        page="battery-thermal-model.html", img="thermal_temp_plot.jpg", size=(2000, 918), width=900,
        margins=(30, 84, 30, 84),
        caption="Single-cell temperature over a 22-minute endurance run",
        label="Simulated cell temperature over a 22-minute endurance run, with handwritten labels: "
              "the curve is steep at the start when the cell is full, gentler in the middle where "
              "DCIR is lowest, and steep again as the cell empties",
        notes=[
            dict(at=(40, 552), lines=["steep start (full cell)"], arrow=((170, 526), ("p", 335, 712), -12)),
            dict(at=(560, 552), anchor="middle", lines=["gentle middle: DCIR is lowest"],
                 arrow=((556, 526), ("p", 1156, 392), 5)),
            dict(at=(920, 44), anchor="end", lines=["steep again as it empties"],
                 arrow=((800, 58), ("p", 1600, 150), -30)),
        ],
    ),
]


def arrow_path(start, end, bend):
    (x1, y1), (x2, y2) = start, end
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    cx = (x1 + x2) / 2 - dy / dist * bend
    cy = (y1 + y2) / 2 + dx / dist * bend
    ang = math.atan2(y2 - cy, x2 - cx)
    head = []
    for off in (0.5, -0.5):
        head.append((x2 - 18 * math.cos(ang + off), y2 - 18 * math.sin(ang + off)))
    r = lambda v: format(round(v, 1), "g")
    return (f"M{r(x1)} {r(y1)} Q{r(cx)} {r(cy)} {r(x2)} {r(y2)} "
            f"M{r(head[0][0])} {r(head[0][1])} L{r(x2)} {r(y2)} L{r(head[1][0])} {r(head[1][1])}")


def build(fig, grid=False):
    w0, h0 = fig["size"]
    left, top, right, bottom = fig["margins"]
    w = fig["width"]
    s = w / w0
    h = round(h0 * s)
    vw, vh = w + left + right, h + top + bottom
    out = [f'<svg viewBox="0 0 {vw} {vh}" role="img" aria-label="{html.escape(fig["label"])}">',
           f'<image class="n-photo" href="../img/{fig["img"]}" x="{left}" y="{top}" width="{w}" height="{h}"/>']
    for x, rot in ((left - 30, -8), (left + w - 56, 7)):
        out.append(f'<rect class="n-tape" x="{x}" y="{top - 12}" width="86" height="26" '
                   f'transform="rotate({rot} {x + 43} {top + 1})"/>')
    for n in fig["notes"]:
        x, y = n["at"]
        anchor = f' text-anchor="{n["anchor"]}"' if n.get("anchor") else ""
        for line in n["lines"]:
            out.append(f'<text class="n-text" x="{x}" y="{y}"{anchor}>{html.escape(line)}</text>')
            y += 30
        if n.get("small"):
            out.append(f'<text class="n-text n-small" x="{x}" y="{y - 4}"{anchor}>{html.escape(n["small"])}</text>')
        if n.get("arrow"):
            start, target, bend = n["arrow"]
            if target[0] == "p":
                target = (left + target[1] * s, top + target[2] * s)
            out.append(f'<path class="n-arrow" d="{arrow_path(start, target, bend)}"/>')
    if grid:  # faint 100-unit grid, preview only
        for gx in range(0, vw, 100):
            out.append(f'<path d="M{gx} 0V{vh}" stroke="#0af" stroke-width="1" opacity=".5"/>'
                       f'<text x="{gx + 2}" y="12" font-size="12" fill="#0af">{gx}</text>')
        for gy in range(0, vh, 100):
            out.append(f'<path d="M0 {gy}H{vw}" stroke="#0af" stroke-width="1" opacity=".5"/>'
                       f'<text x="2" y="{gy + 12}" font-size="12" fill="#0af">{gy}</text>')
    out.append("</svg>")
    return (f'<figure class="fig-hero note-fig">{"".join(out)}'
            f'<figcaption>{html.escape(fig["caption"])}</figcaption></figure>')


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = pathlib.Path(sys.argv[sys.argv.index("--preview") + 1])
        preview.mkdir(parents=True, exist_ok=True)
    grid = "--grid" in sys.argv
    for fig in FIGS:
        page = ROOT / "projects" / fig["page"]
        with page.open(encoding="utf-8", newline="") as f:  # keep the file's own line endings
            text = f.read()
        pattern = re.compile(r'^<figure[^\r\n]*img/' + re.escape(fig["img"]) + r'"[^\r\n]*</figure>(?=\r?$)', re.M)
        if not pattern.search(text):
            print("NOT FOUND:", fig["page"], fig["img"])
            continue
        with page.open("w", encoding="utf-8", newline="") as f:
            f.write(pattern.sub(lambda m: build(fig), text, count=1))
        print("updated", fig["page"], fig["img"])
        if preview:
            css = (ROOT / "style.css").as_uri()
            body = build(fig, grid).replace("../img/", (ROOT / "img").as_uri() + "/")
            (preview / (pathlib.Path(fig["img"]).stem + ".html")).write_text(
                f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{css}">'
                f'<body><main class="wrap">{body}</main>', encoding="utf-8")


main()
