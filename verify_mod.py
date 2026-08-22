#!/usr/bin/env python3
"""Cross-checks the mod's Java against its resources.

The failure mode this is built to catch is drift: an item registered in Java
with no model or lang key, an animation name referenced from a controller that
the .animation.json does not define, a recipe pointing at an item that was
renamed. None of those fail the build — they fail silently at runtime.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "src/main/resources")
JAVA = os.path.join(HERE, "src/main/java/com/fieldgear")
NS = "fieldgear"

errors, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def load(rel):
    with open(os.path.join(RES, rel)) as fh:
        return json.load(fh)


def read_java(rel):
    with open(os.path.join(JAVA, rel)) as fh:
        return fh.read()


# ------------------------------------------------------------ 1. all JSON ---
for dirpath, _, files in os.walk(RES):
    for f in files:
        if f.endswith(".json"):
            p = os.path.join(dirpath, f)
            try:
                json.load(open(p))
                checks += 1
            except Exception as e:
                errors.append(f"invalid JSON {os.path.relpath(p, RES)}: {e}")

# ------------------------------------------- 2. registered ids vs resources --
items_java = read_java("common/init/ModItems.java")
# registrations go through the simple/plate/goggles/armour helpers
registered = set()
for helper in ("simple", "plate", "goggles", "armour"):
    registered |= set(re.findall(helper + r'\("([a-z0-9_]+)"', items_java))
registered |= set(re.findall(r'ITEMS\.register\("([a-z0-9_]+)"', items_java))
ok(len(registered) >= 16, f"only {len(registered)} items parsed out of ModItems.java")

# armour(...) calls carry the model basename as the 4th argument
armour_models = dict(re.findall(
    r'armour\("([a-z0-9_]+)",\s*GearMaterial\.[A-Z]+,\s*ArmorItem\.Type\.[A-Z]+,\s*"([a-z0-9_]+)"',
    items_java))
ok(len(armour_models) == 7, f"expected 7 armour pieces, parsed {len(armour_models)}")

lang = load(f"assets/{NS}/lang/en_us.json")
for item in sorted(registered):
    ok(os.path.exists(f"{RES}/assets/{NS}/models/item/{item}.json"),
       f"{item}: no item model")
    ok(f"item.{NS}.{item}" in lang, f"{item}: no lang key")

# ------------------------------------------------- 3. models -> textures ----
for f in sorted(os.listdir(f"{RES}/assets/{NS}/models/item")):
    model = load(f"assets/{NS}/models/item/{f}")
    for _, tex in model.get("textures", {}).items():
        ns, path = tex.split(":", 1)
        ok(ns == NS, f"{f}: texture in unexpected namespace {ns}")
        ok(os.path.exists(f"{RES}/assets/{ns}/textures/{path}.png"),
           f"{f}: missing texture {tex}")
    parent = model.get("parent", "")
    if parent.startswith(f"{NS}:"):
        ok(os.path.exists(f"{RES}/assets/{NS}/models/{parent.split(':', 1)[1]}.json"),
           f"{f}: missing parent model {parent}")

# --------------------------------------- 4. armour models -> geo + texture ---
used_models = set(armour_models.values())
for m in sorted(used_models):
    ok(os.path.exists(f"{RES}/assets/{NS}/geo/item/armor/{m}.geo.json"),
       f"{m}: missing geometry")
    ok(os.path.exists(f"{RES}/assets/{NS}/textures/item/armor/{m}.png"),
       f"{m}: missing texture")
    ok(os.path.exists(f"{RES}/assets/{NS}/animations/item/armor/{m}.animation.json"),
       f"{m}: missing animation file (GeoModel.getAnimationResource points at it)")

# ------------------------------- 5. Java animation names exist in the files --
armour_java = read_java("common/item/GearArmorItem.java")
anim_names = set(re.findall(r'thenPlayAndHold\("([a-z_]+)"\)', armour_java))
ok(anim_names, "no animations referenced from GearArmorItem")

available = {}
for m in used_models:
    data = load(f"assets/{NS}/animations/item/armor/{m}.animation.json")
    available[m] = set(data.get("animations", {}))

# visor animations must exist on whichever helmet carries the has_visor tag
visor_tag = load(f"data/{NS}/tags/items/has_visor.json")["values"]
mount_tag = load(f"data/{NS}/tags/items/goggle_mount.json")["values"]
for entry in visor_tag:
    item = entry.split(":", 1)[1]
    model = armour_models.get(item)
    ok(model is not None, f"has_visor tags {item}, which is not a registered armour piece")
    if model:
        for a in ("helmet_open", "helmet_closed"):
            ok(a in available[model], f"{model}.animation.json missing '{a}' (needed by has_visor)")
for entry in mount_tag:
    item = entry.split(":", 1)[1]
    model = armour_models.get(item)
    ok(model is not None, f"goggle_mount tags {item}, which is not a registered armour piece")
    if model:
        for a in ("nvg_up", "nvg_down"):
            ok(a in available[model], f"{model}.animation.json missing '{a}' (needed by goggle_mount)")

# ------------------------- 6. the nvg bone the renderer hides must exist -----
model_java = read_java("client/model/GearArmorModel.java")
bone = re.search(r'NVG_BONE\s*=\s*"([a-z_]+)"', model_java)
ok(bone is not None, "could not find NVG_BONE in GearArmorModel")
if bone:
    for entry in mount_tag:
        m = armour_models.get(entry.split(":", 1)[1])
        if not m:
            continue
        geo = load(f"assets/{NS}/geo/item/armor/{m}.geo.json")["minecraft:geometry"][0]
        names = {b["name"] for b in geo["bones"]}
        ok(bone.group(1) in names,
           f"{m}.geo.json has no '{bone.group(1)}' bone for the renderer to hide")

# ------------------------------------------------------------- 7. tags ------
for f in sorted(os.listdir(f"{RES}/data/{NS}/tags/items")):
    tag = load(f"data/{NS}/tags/items/{f}")
    ok(tag.get("replace") is False, f"{f}: replace should be false")
    for v in tag["values"]:
        ns, item = v.split(":", 1)
        if ns == NS:
            ok(item in registered, f"{f}: tags unregistered item {v}")

# ----------------------------------------------------------- 8. recipes -----
recipe_root = f"{RES}/data/{NS}/recipes"
compat_count = 0
for dirpath, _, files in os.walk(recipe_root):
    for f in files:
        rel = os.path.relpath(os.path.join(dirpath, f), RES)
        r = load(rel)
        result = r["result"]["item"]
        rns, rid = result.split(":", 1)
        ok(rns == NS and rid in registered, f"{f}: result {result} is not registered")

        conditions = r.get("conditions", [])
        if conditions:
            # either "load this only with FP" or "load this only without FP" —
            # both are mod_loaded, one wrapped in a not
            def gates_on_mod(c):
                if c.get("type") == "forge:mod_loaded":
                    return True
                return (c.get("type") == "forge:not"
                        and c.get("value", {}).get("type") == "forge:mod_loaded")
            ok(any(gates_on_mod(c) for c in conditions),
               f"{f}: has conditions but none of them gate on a mod being loaded")
            if any(c.get("type") == "forge:mod_loaded" for c in conditions):
                compat_count += 1

        ingredients = []
        if "ingredients" in r:
            ingredients = r["ingredients"]
        elif "key" in r:
            ingredients = list(r["key"].values())
        for ing in ingredients:
            item = ing.get("item", "")
            ins, iid = item.split(":", 1)
            if ins == NS:
                ok(iid in registered, f"{f}: ingredient {item} is not registered")
            elif ins == "fracturepoint":
                ok(bool(conditions), f"{f}: uses a Fracture Point item but is not conditioned")

ok(compat_count > 0, "no Fracture Point compat recipes were written")

# ----------------------------------------- 9. mods.toml placeholders --------
props = {}
for line in open(os.path.join(HERE, "gradle.properties")):
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        props[k.strip()] = v.strip()

toml = open(os.path.join(RES, "META-INF/mods.toml")).read()
for placeholder in set(re.findall(r"\$\{([a-z_]+)\}", toml)):
    ok(placeholder in props,
       f"mods.toml uses ${{{placeholder}}} but gradle.properties does not define it")

ok(props.get("mod_id") == NS, "mod_id in gradle.properties does not match the resource namespace")
main_java = read_java("FieldGear.java")
ok(f'MODID = "{NS}"' in main_java, "MODID in FieldGear.java does not match the namespace")

# ------------------------------------------------- 10. soft-dep tag merge ---
# These merges are what hand FP's systems our gear, so each one must exist,
# must not replace FP's own entries, and must name a registered item.
FP_MERGES = {
    "plate_compatible": f"{NS}:scav_chestplate",
    "can_have_goggles": f"{NS}:bastion_helmet",
    "hide_layer": f"{NS}:scav_leggings",
}
for name, expected in FP_MERGES.items():
    path = f"{RES}/data/fracturepoint/tags/items/{name}.json"
    ok(os.path.exists(path), f"missing Fracture Point tag merge: {name}.json")
    if os.path.exists(path):
        t = json.load(open(path))
        ok(t.get("replace") is False,
           f"{name}.json must not set replace:true, or it would wipe FP's own entries")
        ok(expected in t["values"], f"{name}.json does not contain {expected}")
        ok(expected.split(":", 1)[1] in registered,
           f"{name}.json names an unregistered item")

# our plate/goggle recipes must be gated off when FP is installed, or the game
# ends up with two parallel sets of the same thing
for item in ("steel_plate_iii", "ceramic_plate_iv", "aramid_plate_iiia",
             "nvg_goggles", "thermal_goggles"):
    r = load(f"data/{NS}/recipes/{item}.json")
    conds = r.get("conditions", [])
    ok(any(c.get("type") == "forge:not" for c in conds),
       f"{item}: should be gated off when Fracture Point is present")

print(f"{len(registered)} items registered, {len(used_models)} armour models, "
      f"{compat_count} conditional recipes")
print(f"{checks} checks run")
if errors:
    print(f"\n{len(errors)} FAILURES:")
    for e in errors[:25]:
        print(" -", e)
    sys.exit(1)
print("all checks passed")
