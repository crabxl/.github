# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools[woff]", "resvg-py"]
# ///
"""Build the CrabXL logo files.

    uv run logo/build.py

The crab's shell is a block of 3 x 2 cells. `icon` puts the crab in a red tile
for favicons and avatars; `mark` is the red crab alone, used beside the name.
"""

import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = (
    ROOT
    / "crabxl-webpage/node_modules/@fontsource-variable/schibsted-grotesk/files"
    / "schibsted-grotesk-latin-wght-normal.woff2"
)
RED, RED_DARK = "#d2432c", "#f0654c"
INK, INK_DARK = "#16212b", "#e7ecef"


def claw(cx, cy, r, opening, gap):
    """A pincer: a disc with a wedge cut out, opening toward `opening` degrees."""
    a1, a2 = math.radians(opening - gap / 2), math.radians(opening + gap / 2)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    nx = cx + (x1 + x2 - 2 * cx) * 0.05
    ny = cy + (y1 + y2 - 2 * cy) * 0.05
    return f"M{x2:.2f} {y2:.2f}A{r} {r} 0 1 1 {x1:.2f} {y1:.2f}L{nx:.2f} {ny:.2f}Z"


def crab(color, mask_id):
    """The crab in a 120 x 120 box. Only the shell is cut into cells."""
    return f"""<mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="120" height="120">
<rect width="120" height="120" fill="#fff"/>
<path fill="#000" d="M47 50h3v50h-3zM70 50h3v50h-3zM20 73.5h80v3H20z"/>
</mask>
<g fill="{color}" stroke="{color}" stroke-linecap="round">
<path stroke="none" d="{claw(24, 27, 15, -58, 74)}"/>
<path stroke="none" d="{claw(96, 27, 15, -122, 74)}"/>
<path fill="none" stroke-width="8" d="M29 40 37 56M91 40 83 56"/>
<path fill="none" stroke-width="5" d="M55 54 52 43M65 54 68 43"/>
<circle stroke="none" cx="51" cy="39" r="5.5"/><circle stroke="none" cx="69" cy="39" r="5.5"/>
<path fill="none" stroke-width="6" d="M28 66 12 60M28 82 10 84M32 92 16 100M92 66 108 60M92 82 110 84M88 92 104 100"/>
</g>
<rect mask="url(#{mask_id})" fill="{color}" x="24" y="52" width="72" height="46" rx="16"/>"""


def svg(width, height, body, view=None):
    view = view or f"0 0 {width} {height}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="{view}">\n{body}\n</svg>\n'
    )


def icon(radius=26):
    """White crab in a red tile. radius=0 gives a full square for avatars."""
    return svg(
        120,
        120,
        f'<rect width="120" height="120" rx="{radius}" fill="{RED}"/>\n'
        f'<g transform="translate(13 11) scale(0.783)">{crab("#fff", "cells")}</g>',
    )


def mark(color=RED):
    return svg(120, 120, crab(color, "cells"))


def text_paths(text, size, x, baseline):
    """Outline `text` in Schibsted Grotesk Bold. Returns (paths, advance width)."""
    font = TTFont(FONT)
    font = instantiateVariableFont(font, {"wght": 700})
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    paths, cursor = [], x
    for char in text:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
        paths.append(pen.getCommands())
        cursor += glyphs[name].width * scale - size * 0.01
    return paths, cursor - x


def lockup(ink, red, mask_id):
    """Crab beside the name: "Crab" in ink, "XL" in red."""
    size, gap, mark_size = 96, 24, 128
    crab_part, crab_width = text_paths("Crab", size, mark_size + gap, 100)
    xl_part, xl_width = text_paths("XL", size, mark_size + gap + crab_width, 100)
    width = round(mark_size + gap + crab_width + xl_width + 4)
    body = (
        f'<svg x="0" y="0" width="{mark_size}" height="{mark_size}" viewBox="0 0 120 120">'
        f"{crab(red, mask_id)}</svg>\n"
        f'<path fill="{ink}" d="{"".join(crab_part)}"/>\n'
        f'<path fill="{red}" d="{"".join(xl_part)}"/>'
    )
    return svg(width, mark_size, body)


def png(source, path, size):
    import resvg_py

    data = resvg_py.svg_to_bytes(svg_string=source, width=size, height=size)
    path.write_bytes(bytes(data))


def main():
    out = HERE
    (out / "crabxl-icon.svg").write_text(icon(), encoding="utf-8")
    (out / "crabxl-mark.svg").write_text(mark(), encoding="utf-8")
    (out / "crabxl-logo-light.svg").write_text(lockup(INK, RED, "l"), encoding="utf-8")
    (out / "crabxl-logo-dark.svg").write_text(lockup(INK_DARK, RED_DARK, "d"), encoding="utf-8")
    png(icon(0), out / "crabxl-avatar.png", 1024)
    png(icon(), out / "crabxl-icon-180.png", 180)
    print("ok")


if __name__ == "__main__":
    main()
