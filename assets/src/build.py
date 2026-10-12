#!/usr/bin/env python3
"""Builds the pixel-art SVGs used by the profile README.

    python3 assets/src/build.py

Everything is drawn from the character grids below, so editing a sprite means editing text,
not SVG. Output goes to assets/*.svg.
"""
from __future__ import annotations

import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- palette
BG = "#17211B"        # page-dark moss
PANEL = "#1F2C24"
EDGE = "#3E6B4C"      # moss
BONE = "#F7F4EC"
MINT = "#CFE0CC"
SAGE = "#7FA88A"
AMBER = "#E8B04A"
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'

PAL = {
    "K": "#1E1A1D",  # outline
    "H": "#2B201C",  # hair
    "h": "#4A3A31",  # hair highlight
    "S": "#DCA67E",  # skin
    "s": "#C08A63",  # skin shadow
    "B": "#7A5843",  # stubble
    "E": "#1E1A1D",  # eye
    "W": "#F3EDE4",  # eye glint
    "M": "#7A3B2E",  # lip
    "T": "#F7F1E8",  # teeth
    "R": "#C8322B",  # tilak
    "J": "#D9A9A4",  # jacket
    "j": "#BF8C87",  # jacket shadow
    "P": "#A26F6B",  # jacket seam
    "O": "#F2F0EC",  # hoodie
    "o": "#D3CEC6",  # hoodie shadow
    "N": "#3A3A3A",  # print on the hoodie
    # icons
    "G": "#7FA88A", "Y": "#E8B04A", "A": "#5E8A69", "L": "#DDEAF2", "b": "#8A5A3B",
}

# ---------------------------------------------------------------- avatar (32 x 32)
# Left half only; each row is mirrored to make the face symmetric, then OVERRIDES break
# the symmetry where a real face isn't symmetric (hair, highlights, eye glints).
AVATAR_LEFT = [
    "................",  # 0
    "..........KKKKKK",  # 1
    "........KKHHHHHH",  # 2
    ".......KHHHhHHHH",  # 3
    "......KHHHHHHhHH",  # 4
    "......KHHhHHHHHH",  # 5
    ".....KHHHHHHHHHH",  # 6
    ".....KHHHHHHHHHH",  # 7
    ".....KHHHHHHHHHH",  # 8
    "......KHHSSSSSSS",  # 9  hairline
    "......KHSSSSSSSS",  # 10
    ".....KsSKKKKSSSS",  # 11 brows
    ".....KsSSSSSSSSS",  # 12
    ".....KsSSEWSSSSS",  # 13 eyes
    "......KSSEESSSSS",  # 14
    "......KSSSSSSSSs",  # 15 nose
    "......KSSSSSSSss",  # 16
    "......KSSSMSSSSS",  # 17 smile corners
    "......KSSSSMTTTT",  # 18 teeth
    ".......KSSSSMMMM",  # 19
    ".......KSSSSSSSS",  # 20
    "........KsSSSSSS",  # 21 jaw
    ".........KKsSSSS",  # 22
    "..........KKKsSS",  # 23 neck
    "......KKKKKOOKsS",  # 24 hood
    "....KKJJJJKOOOKs",  # 25
    "...KJJJJJJKOoOOO",  # 26
    "..KJJJJJJJJKOOOO",  # 27
    "..KJJJjJJJPKOOOO",  # 28
    ".KJJJJjJJJPKOOOO",  # 29
    ".KJJJJjJJJPKOOOO",  # 30
    ".KJJJJjJJJPKOoOO",  # 31
]
OVERRIDES = {
    # wavier, lopsided hair
    (1, 9): "K", (1, 22): "K", (2, 8): "K", (0, 13): "K", (0, 14): "K", (0, 18): "K",
    (1, 13): "H", (1, 14): "H", (1, 18): "H", (2, 23): "K", (2, 24): ".",
    (3, 20): "h", (4, 10): "h", (5, 22): "h", (6, 17): "h", (7, 12): "h",
    (8, 15): "S", (8, 16): "S", (8, 14): "S",  # hair swept up, forehead shows
    # glint on the same side of both eyes
    (13, 21): "E", (13, 22): "W",
}
BLINK_SKIN = [(13, 9), (13, 10), (13, 21), (13, 22)]
BLINK_LASH = [(14, 9), (14, 10), (14, 21), (14, 22)]


def mirrored(left: list[str]) -> list[list[str]]:
    rows = []
    for line in left:
        assert len(line) == 16, f"bad row width {len(line)}: {line!r}"
        rows.append(list(line + line[::-1]))
    return rows


def avatar_grid() -> list[list[str]]:
    grid = mirrored(AVATAR_LEFT)
    for (r, c), ch in OVERRIDES.items():
        grid[r][c] = ch
    return grid


def rects(grid, x0: float, y0: float, px: float, pal=PAL, skip=".") -> str:
    """Grid -> <rect>s, merging horizontal runs of one colour."""
    out = []
    for r, row in enumerate(grid):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == skip or ch not in pal:
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            out.append(f'<rect x="{x0 + start * px:g}" y="{y0 + r * px:g}" '
                       f'width="{(c - start) * px:g}" height="{px:g}" fill="{pal[ch]}"/>')
    return "".join(out)


def cells(points, ch, x0, y0, px) -> str:
    return "".join(f'<rect x="{x0 + c * px:g}" y="{y0 + r * px:g}" width="{px:g}" '
                   f'height="{px:g}" fill="{PAL[ch]}"/>' for r, c in points)


def backdrop(n: int = 32, seed: int = 7) -> list[list[str]]:
    """Sky, a canopy of trees and a strip of lawn, like the photo."""
    rnd = random.Random(seed)
    pal_keys = {}
    g = [["sky"] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            edge = min(c, n - 1 - c)
            canopy = r < 20 and (r < 9 + rnd.randint(0, 4) or edge < 5 + rnd.randint(0, 3))
            if canopy:
                g[r][c] = rnd.choice(["leaf", "leaf", "leaf2", "leaf3"])
            if r >= 27:
                g[r][c] = "grass" if (r + c) % 3 else "grass2"
            if (r < 4 or edge < 2) and rnd.random() < 0.18:
                g[r][c] = "sky"
    return g


BACK_PAL = {"sky": "#BFD6E6", "leaf": "#3F6B3A", "leaf2": "#2F5530", "leaf3": "#5F8A4A",
            "grass": "#8BAE5A", "grass2": "#7A9E4C"}


def avatar_svg(x0: float, y0: float, px: float, frame: bool = True) -> str:
    size = 32 * px
    parts = []
    if frame:
        # stepped "pixel" frame
        f = px
        parts.append(f'<rect x="{x0 - 2*f:g}" y="{y0 - f:g}" width="{size + 4*f:g}" height="{size + 2*f:g}" fill="{EDGE}"/>')
        parts.append(f'<rect x="{x0 - f:g}" y="{y0 - 2*f:g}" width="{size + 2*f:g}" height="{size + 4*f:g}" fill="{EDGE}"/>')
    parts.append(rects(backdrop(), x0, y0, px, BACK_PAL))
    parts.append(rects(avatar_grid(), x0, y0, px))
    blink = cells(BLINK_SKIN, "S", x0, y0, px) + cells(BLINK_LASH, "K", x0, y0, px)
    blink += cells([(14, 8), (14, 23)], "S", x0, y0, px)
    parts.append(
        f'<g opacity="0">{blink}<animate attributeName="opacity" values="0;1;0" '
        f'keyTimes="0;0.94;0.98" dur="4.5s" calcMode="discrete" repeatCount="indefinite"/></g>')
    return "".join(parts)


# ---------------------------------------------------------------- 5x7 pixel font
FONT_SRC = {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .###.",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": "### .#. .#. .#. .#. .#. ###",
    "J": "..### ...#. ...#. ...#. #..#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# ##..# #.#.# #..## #...# #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# ##.## #...#",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "'": "# # . . . . .",
    ",": ". . . . . # #",
    "!": "# # # # # . #",
    ".": ". . . . . . #",
    " ": "... ... ... ... ... ... ...",
}
FONT = {ch: s.split() for ch, s in FONT_SRC.items()}


def text_width(text: str, px: float) -> float:
    return sum((len(FONT[ch][0]) + 1) * px for ch in text.upper()) - px


def pixel_text(text: str, x: float, y: float, px: float, color: str, shadow: str | None = None) -> str:
    def draw(dx, dy, col):
        out, cx = [], x + dx
        for ch in text.upper():
            glyph = FONT[ch]
            grid = [row.replace("#", "X") for row in glyph]
            out.append(rects(grid, cx, y + dy, px, {"X": col}))
            cx += (len(glyph[0]) + 1) * px
        return "".join(out)
    s = draw(px * 0.8, px * 0.8, shadow) if shadow else ""
    return s + draw(0, 0, color)


# ---------------------------------------------------------------- shared bits
def svg(w: int, h: int, title: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}" shape-rendering="crispEdges">'
            f'<title>{title}</title>{body}</svg>\n')


def stepped_panel(x, y, w, h, fill, step=6, border=None) -> str:
    """A rectangle with notched pixel corners, optionally with a 1-step border."""
    out = []
    if border:
        out.append(f'<rect x="{x + step}" y="{y}" width="{w - 2*step}" height="{h}" fill="{border}"/>')
        out.append(f'<rect x="{x}" y="{y + step}" width="{w}" height="{h - 2*step}" fill="{border}"/>')
        x, y, w, h = x + 3, y + 3, w - 6, h - 6
    out.append(f'<rect x="{x + step}" y="{y}" width="{w - 2*step}" height="{h}" fill="{fill}"/>')
    out.append(f'<rect x="{x}" y="{y + step}" width="{w}" height="{h - 2*step}" fill="{fill}"/>')
    return "".join(out)


def stars(w, h, n, seed, avoid=None) -> str:
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.randrange(8, w - 8, 4), rnd.randrange(8, h - 8, 4)
        boxes = avoid if avoid and isinstance(avoid[0], tuple) else [avoid] if avoid else []
        if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes):
            continue
        col = rnd.choice([EDGE, "#2C4634", SAGE])
        anim = ""
        if i % 5 == 0:
            anim = (f'<animate attributeName="opacity" values="1;0.2;1" dur="{2 + i % 4}s" '
                    f'repeatCount="indefinite"/>')
        out.append(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{col}">{anim}</rect>')
    return "".join(out)


# ---------------------------------------------------------------- header
def build_header() -> str:
    w, h = 1000, 300
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>', stars(w, h, 90, 3, avoid=[(30, 20, 290, 280), (306, 30, 740, 176), (306, 186, 940, 262)])]
    b.append(avatar_svg(52, 38, 7))
    b.append(pixel_text("SNEHAL", 318, 44, 7, BONE, EDGE))
    b.append(pixel_text("MAHESHWARI", 318, 112, 7, BONE, EDGE))
    b.append(f'<text x="318" y="208" font-family=\'{MONO}\' font-size="17" fill="{MINT}">'
             f'I build autonomous AI systems, and run one in production.</text>')
    b.append(f'<text x="318" y="246" xml:space="preserve" font-family=\'{MONO}\' font-size="16" fill="{SAGE}">$ dailyops --status'
             f'<tspan fill="{BONE}">  running every morning since Jul 2026 </tspan>'
             f'<tspan fill="{AMBER}">█<animate attributeName="opacity" values="1;0;1" dur="1.1s" '
             f'calcMode="discrete" repeatCount="indefinite"/></tspan></text>')
    return svg(w, h, "Snehal Maheshwari: I build autonomous AI systems, and run one in production", "".join(b))


# ---------------------------------------------------------------- section headers
def build_section(slug: str, label: str) -> None:
    w, h = 1000, 60
    px = 4
    tw = text_width(label, px)
    body = [f'<rect width="{w}" height="{h}" rx="12" fill="{BG}"/>',
            f'<rect x="22" y="22" width="8" height="16" fill="{AMBER}"/>',
            pixel_text(label, 44, 16, px, BONE, EDGE)]
    # a pixel rule that runs from the label to the right edge
    x = 44 + tw + 24
    while x < w - 24:
        body.append(f'<rect x="{x}" y="28" width="8" height="4" fill="{EDGE}"/>')
        x += 14
    (OUT / f"h-{slug}.svg").write_text(svg(w, h, label.title(), "".join(body)))


# ---------------------------------------------------------------- project cards
ICONS = {
    "robot": [
        "................",
        ".......YY.......",
        ".......KK.......",
        "...KKKKKKKKKK...",
        "..KGGGGGGGGGGK..",
        "..KGWWGGGGWWGK..",
        "..KGWEGGGGWEGK..",
        "..KGGGGGGGGGGK..",
        "..KGGGMMMMGGGK..",
        "..KGGGGGGGGGGK..",
        "...KKKKKKKKKK...",
        ".....KGGGGK.....",
        "...KKGGGGGGKK...",
        "..KGGGGYYGGGGK..",
        "..KGGGGGGGGGGK..",
        "..KKKKKKKKKKKK..",
    ],
    "anchor": [
        "......KKKK......",
        ".....KAAAAK.....",
        ".....KA..AK.....",
        ".....KAAAAK.....",
        "......KAAK......",
        "...KKKKAAKKKK...",
        "...KAAAAAAAAK...",
        "...KKKKAAKKKK...",
        "......KAAK......",
        "......KAAK......",
        ".KK...KAAK...KK.",
        ".KAK..KAAK..KAK.",
        "..KAK.KAAK.KAK..",
        "...KAAKAAKAAK...",
        "....KKAAAAKK....",
        "......KKKK......",
    ],
    "mail": [
        "................",
        "............RR..",
        "............RR..",
        ".KKKKKKKKKKKKKK.",
        ".KWWWWWWWWWWWWK.",
        ".KKWWWWWWWWWWKK.",
        ".KWKWWWWWWWWKWK.",
        ".KWWKWWWWWWKWWK.",
        ".KWWWKWWWWKWWWK.",
        ".KWWWWKKKKWWWWK.",
        ".KWWWWWWWWWWWWK.",
        ".KWWWWWWWWWWWWK.",
        ".KWWWWWWWWWWWWK.",
        ".KKKKKKKKKKKKKK.",
        "................",
        "................",
    ],
    "lens": [
        "................",
        "....KKKKKK......",
        "...KLLLLLLK.....",
        "..KLLWWLLLLK....",
        "..KLWLLLLLLK....",
        "..KLLLLLLLLK....",
        "..KLLLLLLLLK....",
        "..KLLLLLLLLK....",
        "...KLLLLLLK.....",
        "....KKKKKKbK....",
        "..........KbK...",
        "...........KbK..",
        "............KbK.",
        ".............KK.",
        "................",
        "................",
    ],
}
LANG = {"Python": "#3572A5", "Rust": "#DEA584", "TypeScript": "#3178C6"}


def build_card(slug, icon, title, lines, lang, tag) -> None:
    w, h = 480, 180
    b = [stepped_panel(0, 0, w, h, PANEL, step=8, border=EDGE)]
    b.append(stepped_panel(26, 26, 76, 76, BONE, step=4))
    for row in ICONS[icon]:
        assert len(row) == 16, (icon, row)
    b.append(rects(ICONS[icon], 32, 32, 4))
    b.append(f'<text x="124" y="54" font-family=\'{MONO}\' font-size="21" font-weight="700" fill="{BONE}">{title}</text>')
    for i, line in enumerate(lines):
        b.append(f'<text x="124" y="{86 + i * 22}" font-family="-apple-system, BlinkMacSystemFont, '
                 f'Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="{MINT}">{line}</text>')
    b.append(f'<rect x="124" y="141" width="10" height="10" fill="{LANG[lang]}"/>')
    b.append(f'<text x="142" y="151" font-family=\'{MONO}\' font-size="13" fill="{SAGE}">{lang}</text>')
    tw = len(tag) * 8 + 20
    b.append(stepped_panel(w - 26 - tw, 134, tw, 24, "#2C4634", step=3))
    b.append(f'<text x="{w - 26 - tw / 2}" y="151" text-anchor="middle" font-family=\'{MONO}\' '
             f'font-size="12.5" fill="{MINT}">{tag}</text>')
    (OUT / f"card-{slug}.svg").write_text(svg(w, h, title, "".join(b)))


# ---------------------------------------------------------------- lessons terminal
def build_terminal() -> None:
    w, h = 1000, 286
    b = [stepped_panel(0, 0, w, h, "#111814", step=8, border=EDGE)]
    b.append(f'<rect x="3" y="11" width="{w - 6}" height="30" fill="#1F2C24"/><rect x="11" y="3" width="{w - 22}" height="38" fill="#1F2C24"/>')
    for i, col in enumerate(["#C8322B", AMBER, SAGE]):
        b.append(f'<rect x="{24 + i * 22}" y="16" width="12" height="12" fill="{col}"/>')
    b.append(f'<text x="500" y="28" text-anchor="middle" font-family=\'{MONO}\' font-size="13" fill="{SAGE}">~/learned-the-hard-way</text>')
    lines = [
        ("$ cat lessons.md", SAGE),
        ("> A prompt is a request. A check is a guarantee.", BONE),
        ("> A gate nobody can pass gets switched off. Judge only what changed.", BONE),
        ("> A metric that reads zero is usually a missing event, not missing users.", BONE),
        ("> Give agents memory as plain files in git. Read it, edit it, diff it.", BONE),
        ("> Deterministic first. The model adds to a report that already exists.", BONE),
    ]
    for i, (line, col) in enumerate(lines):
        y = 78 + i * 32
        # each line appears in turn, then the block holds before looping
        # Visible by default, hidden only while the animation runs, so a renderer without SMIL
        # still shows every line.
        appear = (0.4 + i * 0.5) / 4
        b.append(f'<text x="34" y="{y}" font-family=\'{MONO}\' font-size="16" fill="{col}">{line}'
                 f'<animate attributeName="opacity" values="0;1" keyTimes="0;{appear:.3f}" calcMode="discrete" '
                 f'dur="4s" fill="freeze"/></text>')
    y = 78 + len(lines) * 32
    b.append(f'<text x="34" y="{y}" font-family=\'{MONO}\' font-size="16" fill="{SAGE}">$ <tspan fill="{AMBER}">█'
             f'<animate attributeName="opacity" values="1;0;1" dur="1.1s" calcMode="discrete" '
             f'repeatCount="indefinite"/></tspan></text>')
    (OUT / "lessons.svg").write_text(svg(w, h, "Lessons learned the hard way", "".join(b)))


# ---------------------------------------------------------------- stack
def build_stack() -> None:
    rows = [["Python", "FastAPI", "TypeScript", "Vue / Nuxt", "PostgreSQL"],
            ["Rust", "Claude Code", "Gemini", "Docker", "systemd"]]
    w, h = 1000, 104
    b = []
    for r, items in enumerate(rows):
        widths = [len(t) * 9 + 34 for t in items]
        total = sum(widths) + 14 * (len(items) - 1)
        x = (w - total) / 2
        for t, cw in zip(items, widths):
            y = 6 + r * 50
            b.append(stepped_panel(x, y, cw, 40, PANEL, step=4, border=EDGE))
            b.append(f'<text x="{x + cw / 2}" y="{y + 26}" text-anchor="middle" font-family=\'{MONO}\' '
                     f'font-size="15" fill="{BONE}">{t}</text>')
            x += cw + 14
    (OUT / "stack.svg").write_text(svg(w, h, "Stack: " + ", ".join(sum(rows, [])), "".join(b)))


# ---------------------------------------------------------------- footer
def tree(cx: int, base: int, size: int, rnd) -> list[tuple[int, int, str]]:
    pts = []
    trunk_h = size // 2 + 1
    for y in range(base - trunk_h, base):
        pts.append((y, cx, "b"))
    r = size
    cy = base - trunk_h - r + 2
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r - 1, cx + r + 2):
            if (x - cx) ** 2 / (r + 1) ** 2 + (y - cy) ** 2 / r ** 2 <= 1 + rnd.random() * 0.25:
                shade = "f2" if x < cx - r // 3 and y > cy else ("f3" if x > cx and y < cy else "f1")
                pts.append((y, x, shade))
    return pts


def build_footer() -> None:
    px, cols, rows = 5, 200, 30
    rnd = random.Random(11)
    g = [["."] * cols for _ in range(rows)]
    for c in range(cols):
        for r in range(rows - 4, rows):
            g[r][c] = "g1" if (r + c) % 4 else "g2"
    for cx in [8, 22, 38, 150, 166, 184, 196]:
        for y, x, ch in tree(cx, rows - 4, rnd.randint(4, 6), rnd):
            if 0 <= y < rows and 0 <= x < cols:
                g[y][x] = ch
    pal = {"g1": "#3F6B3A", "g2": "#355C31", "b": "#5A3D2B", "f1": "#3F6B3A", "f2": "#2F5530", "f3": "#5F8A4A"}

    def run_rects(grid):
        out = []
        for r, row in enumerate(grid):
            c = 0
            while c < len(row):
                ch = row[c]
                if ch == ".":
                    c += 1
                    continue
                s = c
                while c < len(row) and row[c] == ch:
                    c += 1
                out.append(f'<rect x="{s * px}" y="{r * px}" width="{(c - s) * px}" height="{px}" fill="{pal[ch]}"/>')
        return "".join(out)

    w, h = cols * px, rows * px
    msg = "THANKS FOR STOPPING BY!"
    tw = text_width(msg, 4)
    body = [f'<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>', stars(w, h - 30, 30, 5, avoid=(200, 0, 800, 150)),
            run_rects(g), pixel_text(msg, (w - tw) / 2, 52, 4, BONE, EDGE)]
    (OUT / "footer.svg").write_text(svg(w, h, "Thanks for stopping by", "".join(body)))


def main() -> None:
    # The version is in the filename because GitHub caches README images by URL. Bump it
    # (and the README reference) whenever the portrait changes, or visitors keep the old one.
    (OUT / "header-v2.svg").write_text(build_header())
    build_section("building", "WHAT I'M BUILDING")
    build_section("lessons", "LEARNED THE HARD WAY")
    build_section("stack", "STACK")
    build_card("dailyops", "robot", "allernote-dailyops",
               ["The self-running ops agent behind", "AllerNote: planner, gate, watchdog."],
               "Python", "case study")
    build_card("anchorleg", "anchor", "anchorleg",
               ["Keeps headless coding agents working", "when an account hits its limit."],
               "Rust", "CLI")
    build_card("unimail", "mail", "unimail",
               ["One API to fetch and parse email from", "Gmail, Outlook and IMAP."],
               "TypeScript", "SDK")
    build_card("ospf", "lens", "OSPF",
               ["Find beginner-friendly open source", "projects to contribute to."],
               "TypeScript", "web app")
    build_terminal()
    build_stack()
    build_footer()
    print("built:", ", ".join(sorted(p.name for p in OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
