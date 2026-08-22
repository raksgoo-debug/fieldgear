#!/usr/bin/env python3
"""Emit the standalone mod's resource tree.

Takes the generated geometry and textures and rehomes them under the mod's own
namespace, then writes everything a Forge mod needs alongside: item models,
lang, tags, and recipes. Recipes come in two flavours — plain vanilla crafting,
and Fracture Point ballistics-bench versions gated behind a Forge
`mod_loaded` condition so they only appear when that mod is present.
"""

import json
import os
import shutil

import helmets

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "out")                 # generated geo + textures
MOD = os.path.dirname(HERE)                     # the mod project (tools/..)
NS = "fieldgear"
RES = os.path.join(MOD, "src/main/resources")

# id -> (model, slot, display name, armour material)
ITEMS = {
    "bastion_helmet": ("bastion", "HELMET", "Bastion Helmet", "COMPOSITE"),
    "k63_helmet":     ("k63", "HELMET", "K63 Helmet", "STEEL"),
    "untar_helmet":   ("untar", "HELMET", "UNTAR Helmet", "ARAMID"),
}

PLATES = {
    "steel_plate_iii":   ("Steel Plate (III)", 3, 260),
    "ceramic_plate_iv":  ("Ceramic Plate (IV)", 4, 200),
    "aramid_plate_iiia": ("Aramid Plate (IIIA)", 2, 320),
}

GOGGLES = {
    "nvg_goggles":     ("Night Vision Goggles", "NIGHT_VISION"),
    "thermal_goggles": ("Thermal Goggles", "THERMAL"),
}

MATERIALS = {
    "raw_fibre":     "Raw Fibre",
    "woven_aramid":  "Woven Aramid",
    "ceramic_tile":  "Ceramic Tile",
    "steel_billet":  "Steel Billet",
}

MODELS = ["bastion", "k63", "untar"]

# Vanilla-crafting fallbacks: shaped recipes so the mod stands alone.
VANILLA_RECIPES = {
    "k63_helmet":     (["SSS", "S S"], {"S": "fieldgear:steel_billet"}),
    "untar_helmet":   (["AAA", "A A"], {"A": "fieldgear:woven_aramid"}),
    "bastion_helmet": (["ACA", "A A"], {"A": "fieldgear:woven_aramid",
                                        "C": "fieldgear:ceramic_tile"}),
    "steel_plate_iii":    (["SS", "SS"], {"S": "fieldgear:steel_billet"}),
    "ceramic_plate_iv":   (["CC", "CC"], {"C": "fieldgear:ceramic_tile"}),
    "aramid_plate_iiia":  (["AA", "AA"], {"A": "fieldgear:woven_aramid"}),
    "nvg_goggles":        ([" G ", "SRS"], {"G": "minecraft:glass_pane",
                                            "S": "fieldgear:steel_billet",
                                            "R": "minecraft:redstone"}),
    "thermal_goggles":    ([" G ", "SRS"], {"G": "minecraft:amethyst_shard",
                                            "S": "fieldgear:steel_billet",
                                            "R": "minecraft:redstone_block"}),
    "raw_fibre":          (["SS", "SS"], {"S": "minecraft:string"}),
    "woven_aramid":       (["FF", "FF"], {"F": "fieldgear:raw_fibre"}),
    "ceramic_tile":       (["CC", "CC"], {"C": "minecraft:terracotta"}),
    "steel_billet":       (["II", "II"], {"I": "minecraft:iron_ingot"}),
}

# When Fracture Point is installed, offer its bench recipes using its materials.
FP_BENCH = {
    "bastion_helmet": ([("fracturepoint:woven_kevlar", 2),
                        ("fracturepoint:composite_material", 1),
                        ("fracturepoint:polymer_compound", 1)], 260),
    "k63_helmet":     ([("fracturepoint:steel_plate", 2),
                        ("fracturepoint:woven_kevlar", 2)], 220),
    "untar_helmet":   ([("fracturepoint:kevlar_fiber", 3),
                        ("fracturepoint:woven_kevlar", 1)], 170),
}


def write(rel, data, raw=False):
    path = os.path.join(RES, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(data if raw else json.dumps(data, indent=2) + "\n")


def main():
    for sub in ("assets", "data"):
        shutil.rmtree(os.path.join(RES, sub), ignore_errors=True)

    # ---- geometry + textures, rehomed into our namespace
    for m in MODELS:
        src_geo = f"{GEN}/assets/fracturepoint/geo/item/armor/{m}.geo.json"
        geo = json.load(open(src_geo))
        os.makedirs(f"{RES}/assets/{NS}/geo/item/armor", exist_ok=True)
        with open(f"{RES}/assets/{NS}/geo/item/armor/{m}.geo.json", "w") as fh:
            json.dump(geo, fh, indent=2)
        os.makedirs(f"{RES}/assets/{NS}/textures/item/armor", exist_ok=True)
        shutil.copy(f"{GEN}/assets/fracturepoint/textures/item/armor/{m}.png",
                    f"{RES}/assets/{NS}/textures/item/armor/{m}.png")

    # ---- animations
    # Every model gets an animation file, even the static ones. GeckoLib
    # resolves the file lazily, but shipping a stub for each keeps a missing
    # resource from ever being a possibility.
    idle = {"format_version": "1.8.0",
            "animations": {"idle": {"loop": "loop", "animation_length": 0.1, "bones": {}}}}
    specific = {"k63": helmets.K63_ANIMATION, "bastion": helmets.BASTION_ANIMATION}
    for m in MODELS:
        write(f"assets/{NS}/animations/item/armor/{m}.animation.json", specific.get(m, idle))

    # ---- base item model: renders the GeckoLib model instead of a sprite.
    #
    # These transforms assume GearItemRenderer has already pulled the geometry
    # down onto the origin (MODEL_CENTRE_Y). Without that the helmet is about
    # 1.8 blocks up when the rotation below is applied, the rotation swings it
    # out of the slot, and no translation here can put it back — vanilla builds
    # the transform as T*R*S, so the rotation happens about the origin before
    # the translation is applied.
    #
    # `gui` is the one that matters: a three-quarter view, turned so the helmet
    # is seen from its front-left rather than square on, which is what reads as
    # a helmet at 16 pixels.
    #
    # Y is 145, not 215. The GUI camera looks down -z at the model's +z side,
    # and these helmets face -z, so a rotation under 90 degrees shows the back
    # of the helmet. Past 90 it swings the front round to face the viewer, and
    # 145 lands it turned to its left. X 25 tips the crown toward the camera.
    write(f"assets/{NS}/models/item/gear_base.json", {
        "parent": "builtin/entity",
        "display": {
            "gui": {"rotation": [25, 145, 0], "translation": [0, 0, 0],
                    "scale": [0.92, 0.92, 0.92]},
            "thirdperson_righthand": {"rotation": [12, 0, 0], "translation": [0, 3.5, 0.5],
                                      "scale": [0.55, 0.55, 0.55]},
            "thirdperson_lefthand": {"rotation": [12, 0, 0], "translation": [0, 3.5, 0.5],
                                     "scale": [0.55, 0.55, 0.55]},
            "firstperson_righthand": {"rotation": [0, -50, 0], "translation": [0.5, 3.2, 0.5],
                                      "scale": [0.62, 0.62, 0.62]},
            "firstperson_lefthand": {"rotation": [0, 50, 0], "translation": [0.5, 3.2, 0.5],
                                     "scale": [0.62, 0.62, 0.62]},
            "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
            "head": {"rotation": [0, 180, 0], "translation": [0, 14.5, 0],
                     "scale": [1.0, 1.0, 1.0]},
            "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0],
                      "scale": [0.9, 0.9, 0.9]},
        },
    })
    for i in ITEMS:
        write(f"assets/{NS}/models/item/{i}.json", {"parent": f"{NS}:item/gear_base"})
    # plain sprite items
    for i in list(PLATES) + list(GOGGLES) + list(MATERIALS):
        write(f"assets/{NS}/models/item/{i}.json",
              {"parent": "item/generated", "textures": {"layer0": f"{NS}:item/{i}"}})

    # ---- lang
    lang = {
        f"itemGroup.{NS}.gear": "Field Gear",
        f"key.categories.{NS}": "Field Gear",
        f"key.{NS}.toggle_visor": "Toggle Visor / NVGs",
        f"key.{NS}.remove_gear": "Remove Goggles / Plate",
        f"{NS}.tooltip.plates": "Plates: %s/%s",
        f"{NS}.tooltip.plate_slot": "  %s - %s%%",
        f"{NS}.tooltip.no_plates": "No plates fitted",
        f"{NS}.tooltip.goggles": "Fitted: %s",
        f"{NS}.tooltip.goggles_empty": "Goggle mount empty",
        f"{NS}.tooltip.visor": "Visor can be raised",
        f"{NS}.msg.plate_inserted": "Plate inserted",
        f"{NS}.msg.plate_full": "No free plate slots",
        f"{NS}.msg.plate_removed": "Plate removed",
        f"{NS}.msg.goggles_installed": "Goggles installed",
        f"{NS}.msg.goggles_removed": "Goggles removed",
        f"{NS}.msg.no_mount": "This helmet has no goggle mount",
    }
    for i, (_, _, name, _) in ITEMS.items():
        lang[f"item.{NS}.{i}"] = name
    for i, (name, _, _) in PLATES.items():
        lang[f"item.{NS}.{i}"] = name
    for i, (name, _) in GOGGLES.items():
        lang[f"item.{NS}.{i}"] = name
    for i, name in MATERIALS.items():
        lang[f"item.{NS}.{i}"] = name
    write(f"assets/{NS}/lang/en_us.json", lang)

    # ---- our own tags
    # This mod ships helmets only, so the plate system needs a host chestplate
    # from somewhere. Netherite is the same choice Fracture Point makes.
    write(f"data/{NS}/tags/items/plate_compatible.json",
          {"replace": False, "values": ["minecraft:netherite_chestplate"]})
    write(f"data/{NS}/tags/items/goggle_mount.json",
          {"replace": False, "values": [f"{NS}:bastion_helmet"]})
    write(f"data/{NS}/tags/items/has_visor.json",
          {"replace": False, "values": [f"{NS}:k63_helmet"]})
    write(f"data/{NS}/tags/items/plates.json",
          {"replace": False, "values": [f"{NS}:{p}" for p in PLATES]})
    write(f"data/{NS}/tags/items/goggles.json",
          {"replace": False, "values": [f"{NS}:{g}" for g in GOGGLES]})

    # ---- soft-dep: tag files in OUR jar merge into Fracture Point's tags.
    # This is what hands FP's own systems our gear:
    #   plate_compatible  -> FP attaches its plate capability to any chestplate,
    #                        so its plates, HUD, removal screen and speed
    #                        penalty all start working on our rig
    #   can_have_goggles  -> WBArmorItem.canHaveGoggles is tag-driven, so FP
    #                        goggles mount into our helmet, its battery drains
    #                        them and its vision handler drives the effect
    write("data/fracturepoint/tags/items/can_have_goggles.json",
          {"replace": False, "values": [f"{NS}:bastion_helmet"]})

    # ---- recipes: vanilla shaped
    # Our own plates and goggles exist so the mod stands alone. With Fracture
    # Point installed its equivalents drive everything, so ours are gated off
    # rather than sitting in the game as dead duplicates.
    fp_replaces = set(PLATES) | set(GOGGLES)
    for result, (pattern, keys) in VANILLA_RECIPES.items():
        recipe = {
            "type": "minecraft:crafting_shaped",
            "pattern": pattern,
            "key": {k: {"item": v} for k, v in keys.items()},
            "result": {"item": f"{NS}:{result}"},
        }
        if result in fp_replaces:
            recipe["conditions"] = [{
                "type": "forge:not",
                "value": {"type": "forge:mod_loaded", "modid": "fracturepoint"},
            }]
        write(f"data/{NS}/recipes/{result}.json", recipe)

    # ---- recipes: Fracture Point bench, only loaded when that mod is present
    for result, (ings, t) in FP_BENCH.items():
        write(f"data/{NS}/recipes/compat/fp_{result}.json", {
            "type": "fracturepoint:ballistics_bench",
            "conditions": [{"type": "forge:mod_loaded", "modid": "fracturepoint"}],
            "ingredients": [({"item": it, "count": c} if c > 1 else {"item": it})
                            for it, c in ings],
            "result": {"item": f"{NS}:{result}"},
            "processTime": t,
        })

    write("pack.mcmeta", {"pack": {"description": "Field Gear", "pack_format": 15}})
    print(f"resources written to {RES}")


if __name__ == "__main__":
    main()
