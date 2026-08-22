# Field Gear

A standalone Forge 1.20.1 mod: faceted 3D armour with insertable ballistic
plates, mountable night vision, and a flip-up visor. Fracture Point is an
optional dependency — present, it adds bench recipes; absent, everything falls
back to vanilla crafting.

## Why standalone

Fracture Point's `ArmorPackLoader` reads a hardcoded path
(`assets/fracturepoint/fracturepoint_packs/index.json`) from inside its own jar,
and `ArmorPackRegistry` exposes only `registerBundledPacks()` — no hook to
register a pack from another mod. Items therefore cannot be injected into it
from outside, so this mod registers its own.

What *can* cross the boundary is data — and it turns out that is enough to
hand most of FP's own systems this mod's gear.

## Reusing Fracture Point's systems

Most of FP's gear systems are gated on **tags and NBT, not on its item classes**,
so with FP installed this mod stops running its own duplicates and lets FP drive.
Checked against 3.0.0-PT2:

| FP system | Gate | Works on our gear? |
|---|---|---|
| `ArmorPlateCapabilityHandler` | `instanceof ArmorItem` + type `CHESTPLATE` | **Yes** — any chestplate. `#plate_compatible` already lists `minecraft:netherite_chestplate` |
| `WBArmorItem.canHaveGoggles` | `stack.is(CAN_HAVE_GOGGLES) \|\| config` | **Yes** — pure tag, plus a config list |
| `GoggleMounting` | no `instanceof` at all | **Yes** |
| `HelmetBatteryTickHandler` | static NBT helpers, no `instanceof` | **Yes** — batteries drain normally |
| `HelmetVisionHandler` | no `instanceof` | **Yes** — NVG/thermal vision just works |
| `WarbornGoggleMountLayer` | `instanceof WBArmorItem` | **No** — FP will not *draw* goggles on our helmet |
| `ToggleHelmetTopPacket` | `instanceof WBArmorItem` | **No** — our visor toggle stays ours |
| `GoggleTooltip` | `instanceof WBArmorItem` | No — cosmetic only |

So with Fracture Point present:

- `bastion_helmet` is tagged into `#fracturepoint:can_have_goggles`, so FP
  goggles mount into it, its battery powers them and its vision handler runs.
- This mod's own plate/goggle handlers switch off
  (`FracturePointCompat.useOwnGearSystems()`), so nothing absorbs damage twice,
  and its own plate/goggle *items* are gated out of the recipe book with a
  `forge:not` + `forge:mod_loaded` condition rather than sitting there as
  duplicates.
- Because FP's render layer is class-gated, this mod draws the goggle hardware
  itself: `GearArmorModel` shows the `nvg` bone when FP's `InsertedGoggles` NBT
  is present on the helmet. One caveat — FP tracks *raised/lowered* as
  per-player state keyed by UUID, not on the stack, so the modelled goggles sit
  in the lowered position whenever a set is mounted rather than animating with
  FP's toggle.

Without Fracture Point, this mod's own plate and goggle systems run instead and
everything falls back to vanilla crafting.

Two other data routes are also in use:

- **Recipes** under `data/fieldgear/recipes/compat/` carry a
  `forge:mod_loaded` condition, so the ballistics bench versions only load when
  Fracture Point is installed.
- **Tags merge across mods** rather than one jar winning, which is what makes
  the table above work at all — `data/fracturepoint/tags/` files in *this* jar
  add to FP's tags without touching its source.

## Building

```bash
gradle wrapper --gradle-version 8.8     # once; or just open the folder in IntelliJ
./gradlew build                         # jar lands in build/libs/
./gradlew runClient                     # launch a dev client
```

The Gradle wrapper *jar* is not included (it is a binary). Either run the
`gradle wrapper` command above with a system Gradle, or import the project into
IntelliJ IDEA, which generates it for you.

**This project has not been compiled.** It was authored in an environment
without access to the Forge and Mojang maven repositories, so `gradlew build`
has never run against it. Every Java file is parse-checked (`javac` reports zero
syntax errors; the only diagnostics are unresolved Minecraft/Forge packages,
which is expected without the dependencies), and `verify_mod.py` cross-checks
the Java against the resources. Expect to fix a small number of API mismatches
on the first real compile — the likely spots are listed under *Touch points*
below.

## What is in it

| Item | Notes |
|---|---|
| `bastion_helmet` | Composite tier. Has a shroud — goggles can be fitted. |
| `k63_helmet` | Steel tier. Visor raises and lowers. |
| `untar_helmet` | Aramid tier. |
| `steel_plate_iii`, `ceramic_plate_iv`, `aramid_plate_iiia` | Ballistic plates. |
| `nvg_goggles`, `thermal_goggles` | Mountable optics. |
| `raw_fibre`, `woven_aramid`, `ceramic_tile`, `steel_billet` | Crafting materials. |

Helmets have no inventory sprite: they parent to `builtin/entity` and a
`GeoItemRenderer` draws the 3D model in hand, on the ground and in item frames.

Since the mod ships helmets only, `#fieldgear:plate_compatible` tags
`minecraft:netherite_chestplate` so the plate system has a host. Point that tag
at whatever rig you like.

## The three systems

These are the standalone implementations, used when Fracture Point is absent.

**Shell shapes.** Each dome is a stack of octagonal rings on a spherical
profile — every cube axis-aligned or rotated about Y only. An earlier version
bridged each change of section with 45-degree slabs rotated about X and Z; that
gave a clean profile face-on but left a notch at all four corners where a
sloping slab met a vertical facet. Many small steps have no corners to notch,
and at 16 px per block a step of about a quarter unit reads as smooth.

Helmets sit against a fixed reference: vanilla heads span y 24..32 with the eyes
at about y 28, so a shell whose rim falls below y 27 covers the face.
`tools/fit_check.py` renders each helmet on a plain head with that line marked.

**Plates.** Up to two per compatible chestplate, stored in the stack's NBT so
they travel with the item through chests, death drops and client sync without
needing a capability. `LivingHurtEvent` runs incoming damage through them first;
they soak an amount proportional to their level, wear down doing it, and break
when spent. Damage that bypasses armour bypasses plates too, so a plate carrier
does not quietly become a universal damage sponge. Fit by right-clicking a plate
while wearing the rig; pull the last one back out with the remove key, wear
carried across as item damage.

**Goggles.** Helmets tagged `#fieldgear:goggle_mount` accept goggles, stored the
same way. The NVG hardware is a bone inside `bastion.geo.json` that the renderer
hides when nothing is fitted — one model covers both states rather than shipping
two geometries. Lowering them applies night vision as an ambient, icon-less,
particle-less effect so it reads as optics rather than a potion. Thermal adds
glowing on nearby living entities; note that glowing is a server-side effect and
is therefore visible to *everyone*, not just the wearer — a client-only outline
shader would be the better long-term answer.

**Visor.** Helmets tagged `#fieldgear:has_visor` flip. The cubes sit on a `visor`
bone and `helmet_open` / `helmet_closed` rotate it, the same pattern Fracture
Point uses for Killa and Tagilla.

All three are gated by tags, so adding a new helmet to the goggle system is a
datapack edit, not a code change.

### Controls

- **V** — raise/lower the visor, or stow/deploy fitted goggles
- **B** — remove goggles, or failing that the last fitted plate

The client only ever reports the keypress; the server decides what it means and
owns the NBT, so there is nothing for a modified client to desync.

## Touch points if something does not compile

GeckoLib's API is the most likely source of drift. Everything that talks to it
is in four places:

- `common/item/GearArmorItem.java` — `GeoItem`, `RenderProvider`,
  `AnimationController`, and `DataTickets.ITEMSTACK` for reading per-stack state
  inside an animation predicate.
- `client/model/GearArmorModel.java` — `GeoModel` resource paths, and
  `getAnimationProcessor().getBone("nvg")` for the bone hiding.
- `client/renderer/GearArmorRenderer.java` — `GeoArmorRenderer`.
- `build.gradle` — the `geckolib_version` property.

The armour model is hooked through Forge's own `IClientItemExtensions`, not
GeckoLib's RenderProvider — GeckoLib 4.8 has no
`animatable.client.RenderProvider` and no `GeoItem.makeRenderer`. Every
GeckoLib symbol this mod uses was checked against Fracture Point's compiled
classes, which are built against the same GeckoLib version.

## Renaming the mod

Change `mod_id` and `mod_group_id` in `gradle.properties`, rename the package
folders under `src/main/java`, rename `assets/fieldgear` and `data/fieldgear`,
and update `MODID` in `FieldGear.java`. `verify_mod.py` checks those three stay
in agreement.

## Regenerating the assets

The geometry and textures are generated, not hand-drawn. The generator lives
alongside this project (`scavgen/`): edit a cube list, re-run
`build_models.py`, then `build_mod_assets.py` to rehome everything into this
mod's namespace. See that project's README for the modelling conventions —
1 texel per model unit, and rotated cubes for the faceted silhouettes.

```bash
python3 verify_mod.py      # 237 cross-checks between Java and resources
```
