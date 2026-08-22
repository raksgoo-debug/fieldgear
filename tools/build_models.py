#!/usr/bin/env python3
"""
Field Gear - helmet models and texture sheets.

Generates GeckoLib .geo.json models plus UV-matched texture sheets.
Geometry and UV packing are authored together so the texture can never
drift out of alignment with the model.

Bone rig follows the mod's existing convention (see ratnik.geo.json):
  bipedHead -> armorHead -> Head
  bipedBody -> armorBody -> Body
  biped*Arm -> armor*Arm
  biped*Leg -> armor*Leg / armor*Boot
"""

import json
import math
import os
import random

import geom

from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
GEO_DIR = os.path.join(OUT, "out/assets/fracturepoint/geo/item/armor")
TEX_DIR = os.path.join(OUT, "out/assets/fracturepoint/textures/item/armor")

# ---------------------------------------------------------------- geometry ---
# (bone, name, origin[x,y,z], size[w,h,d], material)
# World space: feet at y=0, head cube spans y 24..32, body 12..24, z -2..2.

# --------------------------------------------------------------- skeletons ---

BASE_BONES = [
    ("bipedHead",      None,             [0, 24, 0]),
    ("armorHead",      "bipedHead",      [0, 24, 0]),
    ("bipedBody",      None,             [0, 24, 0]),
    ("armorBody",      "bipedBody",      [0, 24, 0]),
    ("bipedRightArm",  None,             [-5, 22, 0]),
    ("armorRightArm",  "bipedRightArm",  [-5, 22, 0]),
    ("bipedLeftArm",   None,             [5, 22, 0]),
    ("armorLeftArm",   "bipedLeftArm",   [5, 22, 0]),
    ("bipedRightLeg",  None,             [-2, 12, 0]),
    ("armorRightLeg",  "bipedRightLeg",  [-2, 12, 0]),
    ("armorRightBoot", "bipedRightLeg",  [-2, 12, 0]),
    ("bipedLeftLeg",   None,             [2, 12, 0]),
    ("armorLeftLeg",   "bipedLeftLeg",   [2, 12, 0]),
    ("armorLeftBoot",  "bipedLeftLeg",   [2, 12, 0]),
]

# ------------------------------------------------------------- uv packing ----

FACES = ["north", "east", "south", "west", "up", "down"]

# Texels per model unit. The mod ships everything at 1:1 (= 16 px per block).
TEXELS_PER_UNIT = 1.0


def face_dims(size, face):
    w, h, d = size
    if face in ("north", "south"):
        return w, h
    if face in ("east", "west"):
        return d, h
    return w, d  # up / down


class ShelfPacker:
    """Simple shelf packer; good enough for a few hundred small rects."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.x = 0
        self.y = 0
        self.shelf_h = 0

    def place(self, w, h):
        if w > self.w:
            return None
        if self.x + w > self.w:
            self.x = 0
            self.y += self.shelf_h
            self.shelf_h = 0
        if self.y + h > self.h:
            return None
        pos = (self.x, self.y)
        self.x += w
        self.shelf_h = max(self.shelf_h, h)
        return pos


def unpack(c):
    """(bone, name, origin, size, material, extras)

    extras may hold {"rot": [x,y,z], "pivot": [x,y,z], "decal": {...}}.
    A bare decal dict in slot 5 is still accepted for older definitions.
    """
    extras = c[5] if len(c) > 5 else None
    if extras and "type" in extras:          # legacy: slot 5 was the decal itself
        extras = {"decal": extras}
    return (c[0], c[1], c[2], c[3], c[4], extras or {})


def pack(cubes, tex_size, scale):
    """Return {(cube_index, face): (u, v, uw, uh)} or None if it doesn't fit."""
    rects = []
    for i, size in ((i, unpack(c)[3]) for i, c in enumerate(cubes)):
        for f in FACES:
            fw, fh = face_dims(size, f)
            rects.append((i, f, max(1, math.ceil(fw * scale)), max(1, math.ceil(fh * scale))))
    # tallest first keeps shelves tight
    rects.sort(key=lambda r: (-r[3], -r[2]))
    packer = ShelfPacker(tex_size, tex_size)
    out = {}
    for i, f, w, h in rects:
        pos = packer.place(w, h)
        if pos is None:
            return None
        out[(i, f)] = (pos[0], pos[1], w, h)
    return out


def best_pack(cubes, tex_size):
    """Pack at 1:1 into the smallest standard sheet that fits, up to tex_size."""
    for candidate in (64, 128, 256):
        if candidate > tex_size:
            break
        uv = pack(cubes, candidate, TEXELS_PER_UNIT)
        if uv is not None:
            return uv, candidate
    raise RuntimeError("could not pack UVs at 1:1 — raise the sheet size")


def _unused_best_pack(cubes, tex_size):
    # The mod's own models sit at ~1.00 texels per model unit (measured across
    # ratnik / beta7 / killa / nato_shturmovik: median 1.00). That is standard
    # 16-px-per-block Minecraft density, so pack at 1:1 and never finer.
    uv = pack(cubes, tex_size, TEXELS_PER_UNIT)
    if uv is None:
        raise RuntimeError("could not pack UVs at 1:1 — use a larger sheet")
    return uv, TEXELS_PER_UNIT


# --------------------------------------------------------------- texturing ---

PALETTE = {
    "steel":      (76, 78, 83),
    "steel_dark": (44, 45, 50),
    "rust":       (92, 52, 30),
    "canvas":     (84, 85, 60),
    "tarp":       (56, 70, 74),
    "tape":       (94, 92, 86),
    "leather":    (70, 49, 32),
    "rubber":     (31, 31, 34),
    "cloth":      (74, 72, 52),
    "cloth_dark": (54, 52, 39),
    "canvas_dark": (62, 63, 44),
    "glass":      (24, 36, 30),
    # --- helmet set
    "shell_black":  (57, 58, 63),
    "hardware":     (45, 46, 50),
    "mesh":         (34, 35, 38),
    "olive":        (92, 98, 60),
    "olive_dark":   (72, 77, 47),
    "glass_tint":   (36, 42, 40),
    "un_blue":      (74, 126, 178),
    "un_blue_dark": (58, 103, 150),
    "webbing":      (78, 82, 66),
    "webbing_dark": (44, 46, 40),
}


def clamp(v):
    return max(0, min(255, int(v)))


def shade(c, amt):
    return tuple(clamp(x + amt) for x in c)


FACE_BIAS = {"up": 10, "down": -12, "north": 2, "south": -4, "east": -2, "west": 2}

# Smooth finishes get flat colour plus a soft top-to-bottom gradient and no
# grain at all. Rough ones get the same gradient plus light dithering.
SMOOTH = {"shell_black", "hardware", "olive", "olive_dark", "un_blue",
          "un_blue_dark", "glass", "glass_tint", "steel", "steel_dark",
          "tape", "rubber", "mesh"}


def paint_face(px, rect, mat, face, rng):
    """Paint one face at 16-px-per-block density.

    The look is deliberately clean: a flat base colour with a gentle vertical
    gradient does the shading, and the only other marks are structural ones
    that land on exact rows or columns. Random per-pixel noise reads as dirt at
    this resolution, so smooth materials get none.
    """
    x0, y0, w, h = rect
    base = PALETTE[mat]
    bias = FACE_BIAS[face]
    smooth = mat in SMOOTH
    side = face in ("north", "south", "east", "west")

    for yy in range(h):
        # soft light-from-above gradient down the face
        g = 5 - (11 * yy / (h - 1)) if h > 1 else 0
        for xx in range(w):
            c = shade(base, bias + g + (0 if smooth else rng.randint(-2, 2)))

            if mat == "mesh":                                   # perforated plate
                if (xx + yy) % 2 == 0:
                    c = shade(c, -7)
            elif mat in ("glass", "glass_tint"):
                if yy == 0:
                    c = shade(c, 22)                            # sheen along the top
            elif mat in ("webbing", "webbing_dark"):
                if yy % 2 == 0:
                    c = shade(c, -7)                            # nylon weave
            elif mat == "rubber":
                if yy % 2 == 0:
                    c = shade(c, 6)                             # tread
            elif mat == "tape":
                if yy % 2 == 0:
                    c = shade(c, -8)
            elif mat == "tarp":
                if xx % 2 == 0:
                    c = shade(c, -6)                            # creases
            elif mat == "rust":
                if rng.random() < 0.11:
                    c = shade(c, -11)                           # pitting
                elif rng.random() < 0.07:
                    c = shade(c, 11)                            # flaking
            elif mat in ("canvas", "canvas_dark", "cloth", "cloth_dark"):
                if rng.random() < 0.09:
                    c = shade(c, -7)                            # mottled dirt
            elif mat == "leather":
                if rng.random() < 0.08:
                    c = shade(c, -9)

            px[x0 + xx, y0 + yy] = c

    # a single darker bottom row keeps stacked pieces separated in-game
    if w >= 4 and h >= 4:
        for xx in range(w):
            px[x0 + xx, y0 + h - 1] = shade(px[x0 + xx, y0 + h - 1], -7)

    # weld bead along the top of welded-on scrap
    if mat == "rust" and side and w >= 3 and h >= 3:
        for xx in range(w):
            if rng.random() < 0.6:
                px[x0 + xx, y0] = shade(px[x0 + xx, y0], 14)


# Pixel emblems, drawn at texture scale. '.' keeps the painted face,
# 'X' takes the decal colour, 'o' a darkened version of it.
EMBLEMS = {
    3: ["XXX",
        "XoX",
        "XXX"],
    5: [".XXX.",
        "X...X",
        "X.o.X",
        "X...X",
        ".XXX."],
}


def paint_decal(px, rect, decal):
    """Stamp a small pixel insignia onto one already-painted face."""
    x0, y0, w, h = rect
    if decal["type"] != "roundel":
        raise ValueError(decal["type"])
    col = decal["color"]
    size = 5 if (w - 2 >= 5 and h - 2 >= 5) else 3
    if w < size or h < size:
        return
    art = EMBLEMS[size]
    ox = x0 + (w - size) // 2
    oy = y0 + (h - size) // 2
    for dy, row in enumerate(art):
        for dx, ch in enumerate(row):
            if ch == "X":
                px[ox + dx, oy + dy] = col
            elif ch == "o":
                px[ox + dx, oy + dy] = shade(col, -34)


def build(name, cubes, tex_size, seed, extra_bones=()):
    uvmap, tex_size = best_pack(cubes, tex_size)

    # ---- texture
    img = Image.new("RGBA", (tex_size, tex_size), (0, 0, 0, 0))
    px = img.load()
    rng = random.Random(seed)
    for (i, f), rect in sorted(uvmap.items()):
        paint_face(px, rect, unpack(cubes[i])[4], f, rng)
    for i, c in enumerate(cubes):
        decal = unpack(c)[5].get("decal")
        if decal:
            paint_decal(px, uvmap[(i, decal["face"])], decal)
    os.makedirs(TEX_DIR, exist_ok=True)
    img.save(os.path.join(TEX_DIR, f"{name}.png"))

    # ---- geometry
    bones = {}
    order = []
    for bname, parent, pivot in list(BASE_BONES) + list(extra_bones):
        b = {"name": bname, "pivot": pivot}
        if parent:
            b["parent"] = parent
        bones[bname] = b
        order.append(bname)

    for i, c in enumerate(cubes):
        bone, cname, origin, size, mat, extras = unpack(c)
        uv = {}
        for f in FACES:
            x, y, w, h = uvmap[(i, f)]
            uv[f] = {"uv": [x, y], "uv_size": [w, h]}
        cube = {"origin": [round(v, 4) for v in origin],
                "size": [round(v, 4) for v in size],
                "uv": uv}
        if "rot" in extras:
            # Bedrock cube rotation, Euler XYZ about the cube's own pivot —
            # the convention the mod's shipped models use.
            cube["rotation"] = [round(v, 4) for v in extras["rot"]]
            cube["pivot"] = [round(v, 4) for v in extras["pivot"]]
        bones[bone].setdefault("cubes", []).append(cube)

    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{name}",
                "texture_width": tex_size,
                "texture_height": tex_size,
                "visible_bounds_width": 3,
                "visible_bounds_height": 3.5,
                "visible_bounds_offset": [0, 1.25, 0],
            },
            "bones": [bones[b] for b in order],
        }],
    }
    os.makedirs(GEO_DIR, exist_ok=True)
    with open(os.path.join(GEO_DIR, f"{name}.geo.json"), "w") as fh:
        json.dump(geo, fh, indent=2)

    used = sum(w * h for _, _, w, h in uvmap.values())
    print(f"{name:20s} cubes={len(cubes):3d} tex={tex_size}x{tex_size} "
          f"@{TEXELS_PER_UNIT:g} texel/unit  atlas_used={100.0 * used / (tex_size * tex_size):.1f}%")
    return uvmap, tex_size


if __name__ == "__main__":
    import helmets
    for name, (cubes, size, seed, extra) in helmets.HELMET_MODELS.items():
        build(name, cubes, size, seed, extra)
