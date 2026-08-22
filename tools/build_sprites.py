#!/usr/bin/env python3
"""16x16 inventory sprites for the flat items (plates, goggles, materials).

The armour pieces don't need these — GeckoLib renders those from the 3D model —
but plates, goggles and crafting materials are ordinary sprite items.
Everything is drawn from pixel maps so the icons stay crisp and on-palette.
"""

import os

from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../src/main/resources/assets/fieldgear/textures/item")

T = (0, 0, 0, 0)


def px(hexstr, a=255):
    return (int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16), a)


def draw(name, rows, palette):
    """rows: 16 strings of 16 chars; '.' is transparent."""
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), name
    img = Image.new("RGBA", (16, 16), T)
    p = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                p[x, y] = palette[ch]
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, f"{name}.png"))


# ---------------------------------------------------------------- plates ----
# A curved-top ballistic plate. o=outline, b=body, h=highlight, s=shade,
# p=level pip.
PLATE = [
    "................",
    "....oooooooo....",
    "...ohhhhhhhho...",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbppppbbbo..",
    "..obbbppppbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obssssssssbo..",
    "...obssssssbo...",
    "....obbbbbbo....",
    ".....oooooo.....",
    "................",
]

PLATE_COLOURS = {
    "steel_plate_iii":   ("2b2d31", "6e727a", "8f949d", "4a4d54", "c8ccd2"),
    "ceramic_plate_iv":  ("2a2622", "7d6f5f", "9c8d79", "574c40", "d8cbb4"),
    "aramid_plate_iiia": ("22251c", "5d6647", "78835c", "424933", "b9c49a"),
}

for name, (o, b, h, s, pip) in PLATE_COLOURS.items():
    draw(name, PLATE, {"o": px(o), "b": px(b), "h": px(h), "s": px(s), "p": px(pip)})

# --------------------------------------------------------------- goggles ----
GOGGLES = [
    "................",
    "......oooo......",
    "......obbo......",
    "......obbo......",
    "..oooobbbboooo..",
    ".obbbbbbbbbbbbo.",
    ".obggboobbggbo..",
    ".obggboobbggbo..",
    ".obbbboobbbbbo..",
    ".obllboobllbbo..",
    ".obllboobllbbo..",
    ".obbbboobbbbbo..",
    "..oooo....oooo..",
    "................",
    "................",
    "................",
]

GOGGLE_COLOURS = {
    "nvg_goggles":     ("1b1d20", "3c4046", "23282b", "4e7f4a"),
    "thermal_goggles": ("1b1620", "40384a", "2a2430", "8a4f7d"),
}
for name, (o, b, g, lens) in GOGGLE_COLOURS.items():
    draw(name, GOGGLES, {"o": px(o), "b": px(b), "g": px(g), "l": px(lens)})

# ------------------------------------------------------------- materials ----
draw("raw_fibre", [
    "................",
    "................",
    "...a....a...a...",
    "...aa..aa..aa...",
    "....a..a...a....",
    "....aaaa..aa....",
    ".....aa...a.....",
    "..bbbbbbbbbb....",
    "..bccccccccb....",
    "..bbbbbbbbbb....",
    ".....a...aa.....",
    "....aa...a......",
    "....a...aa......",
    "...aa...a.......",
    "................",
    "................",
], {"a": px("9a8f66"), "b": px("4a4433"), "c": px("6d6449")})

draw("woven_aramid", [
    "................",
    "..oooooooooooo..",
    "..obwbwbwbwbwo..",
    "..owbwbwbwbwbo..",
    "..obwbwbwbwbwo..",
    "..owbwbwbwbwbo..",
    "..obwbwbwbwbwo..",
    "..owbwbwbwbwbo..",
    "..obwbwbwbwbwo..",
    "..owbwbwbwbwbo..",
    "..obwbwbwbwbwo..",
    "..owbwbwbwbwbo..",
    "..obwbwbwbwbwo..",
    "..oooooooooooo..",
    "................",
    "................",
], {"o": px("2c3122"), "b": px("5d6647"), "w": px("77825c")})

draw("ceramic_tile", [
    "................",
    "................",
    "..oooooooooooo..",
    "..ohhhhhhhhhho..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    "..obssssssssbo..",
    "..oooooooooooo..",
    "................",
    "................",
    "................",
], {"o": px("3a332b"), "b": px("8d7f6d"), "h": px("a89a86"), "s": px("6b5f50")})

draw("steel_billet", [
    "................",
    "................",
    "................",
    "................",
    "....oooooooo....",
    "...ohhhhhhhho...",
    "..obbbbbbbbbbo..",
    "..obbbbbbbbbbo..",
    ".obbbbbbbbbbbbo.",
    ".obssssssssssbo.",
    ".oooooooooooooo.",
    "................",
    "................",
    "................",
    "................",
    "................",
], {"o": px("2b2d31"), "b": px("757a83"), "h": px("969ba4"), "s": px("545860")})

print("sprites written to", OUT)
