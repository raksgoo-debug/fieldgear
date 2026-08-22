#!/usr/bin/env python3
"""
Fracture Point / WARBORN - "Scav" improvised raider armour set.

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

SCAV = geom.dome("Head", "shell", -4.30, 4.30, -4.30, 4.30, 26.20, 31.95, "steel",
                 corner=1.10, bevel=1.25, plate=1.30) + [
    # --- helmet: welded steel pot, scrap patches, welding visor -------------
    ("Head", "shell_skirt",  [-4.50, 25.50, -4.50], [9.00, 1.00, 9.00], "steel_dark"),
    geom.tilted("Head", "brim", [-4.10, 26.20, -5.35], [8.20, 1.05, 1.15], "steel_dark",
                rot=[-8, 0, 0]),
    geom.tilted("Head", "patch_l", [-4.75, 27.60, -2.40], [0.70, 2.60, 3.80], "rust",
                rot=[0, 0, 7]),
    geom.tilted("Head", "patch_r", [4.05, 28.10, -1.20], [0.70, 2.10, 3.00], "rust",
                rot=[0, 0, -5]),
    ("Head", "patch_top",    [-2.40, 30.80, -1.20], [3.60, 0.65, 4.00], "rust"),
    geom.tilted("Head", "visor_frame", [-3.60, 24.60, -5.15], [7.20, 2.90, 0.70],
                "steel_dark", rot=[6, 0, 0]),
    geom.tilted("Head", "visor_glass", [-2.60, 25.20, -5.45], [5.20, 1.70, 0.42],
                "glass", rot=[6, 0, 0]),
    geom.tilted("Head", "earcup_r", [-4.95, 26.00, -1.70], [0.80, 2.40, 3.00], "rubber",
                rot=[0, 0, 6]),
    geom.tilted("Head", "earcup_l", [4.15, 26.00, -1.70], [0.80, 2.40, 3.00], "rubber",
                rot=[0, 0, -6]),
    geom.tilted("Head", "rebar_spike", [1.10, 31.60, -0.40], [0.50, 2.90, 0.50], "rust",
                rot=[-9, 0, 6]),
    ("Head", "chin_strap",   [-4.25, 24.15, -3.10], [8.50, 0.65, 6.30], "leather"),
    ("Head", "neck_flap",    [-4.20, 24.30,  3.10], [8.40, 2.20, 1.10], "leather"),

    # --- chest rig: canvas vest, welded scrap plates, pouches ---------------
    ("Body", "vest_lower",   [-4.45, 12.60, -2.65], [8.90, 4.20, 5.30], "canvas_dark"),
    ("Body", "vest_upper",   [-4.25, 16.60, -2.50], [8.50, 5.80, 5.00], "canvas"),
    ("Body", "belt",         [-4.55, 12.30, -2.75], [9.10, 1.10, 5.50], "leather"),
    ("Body", "collar",       [-3.20, 21.90, -2.30], [6.40, 1.50, 4.60], "cloth_dark"),
    ("Body", "plate_front",  [-3.40, 16.10, -3.15], [6.80, 5.60, 0.70], "steel"),
    ("Body", "plate_patch",  [-1.20, 18.40, -3.55], [3.80, 3.00, 0.50], "rust"),
    ("Body", "plate_rivets", [-3.60, 15.60, -3.05], [7.20, 0.60, 0.55], "steel_dark"),
    ("Body", "plate_back",   [-3.20, 16.30,  2.45], [6.40, 5.20, 0.65], "steel"),
    ("Body", "weld_side",    [-4.70, 17.20, -1.40], [0.55, 2.80, 2.80], "rust"),
    ("Body", "strap_r",      [-3.60, 21.60, -2.85], [1.80, 2.60, 0.65], "leather"),
    ("Body", "strap_l",      [ 1.80, 21.60, -2.85], [1.80, 2.60, 0.65], "leather"),
    ("Body", "shoulder_r",   [-3.75, 22.30, -2.55], [2.00, 0.75, 5.10], "leather"),
    ("Body", "shoulder_l",   [ 1.75, 22.30, -2.55], [2.00, 0.75, 5.10], "leather"),
    ("Body", "pouch_1",      [-3.95, 13.10, -4.05], [2.60, 2.80, 1.50], "canvas"),
    ("Body", "flap_1",       [-4.05, 15.70, -4.15], [2.80, 0.70, 1.70], "leather"),
    ("Body", "pouch_2",      [-1.00, 12.90, -4.05], [2.40, 3.10, 1.50], "tarp"),
    ("Body", "flap_2",       [-1.10, 15.80, -4.15], [2.60, 0.70, 1.70], "leather"),
    ("Body", "pouch_3",      [ 1.90, 13.20, -4.00], [2.30, 2.60, 1.45], "canvas"),
    ("Body", "flap_3",       [ 1.80, 15.60, -4.10], [2.50, 0.70, 1.65], "leather"),
    ("Body", "tarp_roll",    [-3.10, 20.30,  2.40], [6.20, 1.80, 1.80], "tarp"),
    ("Body", "canteen",      [ 1.70, 12.90,  2.55], [1.70, 2.70, 1.80], "steel_dark"),
    ("Body", "back_strap",   [-3.30, 16.20,  2.95], [6.60, 0.60, 0.50], "leather"),
    ("Body", "plate_seam",   [-3.40, 18.85, -3.25], [6.80, 0.45, 0.28], "steel_dark"),
    ("Body", "radio",        [ 1.95, 19.30, -3.55], [1.60, 2.20, 0.80], "steel_dark"),
    ("Body", "antenna",      [ 2.55, 21.40, -3.30], [0.35, 2.20, 0.35], "rubber"),
]

UNIFORM = [
    ("armorBody",      "torso",   [-4.05, 12.05, -2.05], [8.10, 12.00, 4.10], "cloth"),
    ("armorBody",      "collar",  [-3.30, 21.60, -2.20], [6.60,  1.80, 4.40], "cloth_dark"),
    ("armorRightArm",  "sleeve",  [-8.05, 12.05, -2.05], [4.10, 11.00, 4.10], "cloth"),
    ("armorRightArm",  "cuff",    [-8.15, 12.00, -2.15], [4.30,  2.20, 4.30], "leather"),
    ("armorLeftArm",   "sleeve",  [ 3.95, 12.05, -2.05], [4.10, 11.00, 4.10], "cloth"),
    ("armorLeftArm",   "cuff",    [ 3.85, 12.00, -2.15], [4.30,  2.20, 4.30], "leather"),
    ("armorRightLeg",  "trouser", [-4.05,  3.00, -2.05], [4.10,  9.10, 4.10], "cloth"),
    ("armorRightLeg",  "knee",    [-4.15,  5.40, -2.50], [4.30,  2.60, 0.60], "rubber"),
    ("armorLeftLeg",   "trouser", [-0.05,  3.00, -2.05], [4.10,  9.10, 4.10], "cloth"),
    ("armorLeftLeg",   "knee",    [-0.15,  5.40, -2.50], [4.30,  2.60, 0.60], "rubber"),
    ("armorRightBoot", "boot",    [-4.10,  0.00, -2.10], [4.20,  3.20, 4.20], "leather"),
    ("armorRightBoot", "sole",    [-4.20, -0.02, -2.20], [4.40,  0.90, 4.60], "rubber"),
    ("armorLeftBoot",  "boot",    [-0.10,  0.00, -2.10], [4.20,  3.20, 4.20], "leather"),
    ("armorLeftBoot",  "sole",    [-0.20, -0.02, -2.20], [4.40,  0.90, 4.60], "rubber"),
]

SHOULDERPADS = [
    # right arm occupies x -8..-4; pad sits on the shoulder crown (~y24)
    ("armorRightArm", "cap",     [-8.45, 23.00, -2.45], [4.90, 1.60, 4.90], "steel"),
    ("armorRightArm", "strap",   [-8.25, 22.35, -2.25], [4.50, 0.70, 4.50], "leather"),
    ("armorRightArm", "skirt",   [-8.60, 20.60, -2.35], [5.20, 1.90, 4.70], "steel"),
    ("armorRightArm", "lip",     [-8.55, 20.20, -2.25], [5.10, 0.55, 4.50], "steel_dark"),
    ("armorRightArm", "patch",   [-8.75, 20.90, -1.30], [0.55, 1.45, 2.60], "rust"),
    # left arm occupies x 4..8
    ("armorLeftArm",  "cap",     [ 3.55, 23.00, -2.45], [4.90, 1.60, 4.90], "steel"),
    ("armorLeftArm",  "strap",   [ 3.75, 22.35, -2.25], [4.50, 0.70, 4.50], "leather"),
    ("armorLeftArm",  "skirt",   [ 3.40, 20.60, -2.35], [5.20, 1.90, 4.70], "steel"),
    ("armorLeftArm",  "lip",     [ 3.45, 20.20, -2.25], [5.10, 0.55, 4.50], "steel_dark"),
    ("armorLeftArm",  "patch",   [ 8.20, 20.90, -1.30], [0.55, 1.45, 2.60], "rust"),
]

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

# Extra grouping bones used by the main set, mirroring ratnik.geo.json.
EXTRA_BONES = {
    "scav": [("Head", "armorHead", [0, 24, 0]), ("Body", "armorBody", [0, 24, 0])],
}

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
    build("scav", SCAV, 256, 20260822, EXTRA_BONES["scav"])
    build("scav_uniform", UNIFORM, 128, 7731)
    build("scav_shoulderpads", SHOULDERPADS, 128, 4412)

    import helmets
    for name, (cubes, size, seed, extra) in helmets.HELMET_MODELS.items():
        build(name, cubes, size, seed, extra)
