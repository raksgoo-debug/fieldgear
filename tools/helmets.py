#!/usr/bin/env python3
"""Three reference helmets for Fracture Point.

Shapes are faceted rather than boxy: each shell is an octagonal dome with a
chamfered crown (see geom.dome), and the fittings carry small deliberate tilts.
That matches how the mod's own models are built — 87% of their cubes are
rotated, which is what gives them smooth silhouettes.

  bastion      - black high-cut shell, NVG shroud, ARC rails, mesh mandible
  zsh          - olive round dome, brow band, front lip, flip-up tinted visor
  peacekeeper  - blue dome with an all-round brim and hanging chin straps

Head cube spans y 24..32, x/z -4..4.
"""

from geom import dome, plain, tilted, corner_posts

# --------------------------------------------------------------- bastion ----
BASTION = (
    dome("Head", "shell", -4.25, 4.25, -4.25, 4.25, 26.30, 32.00, "shell_black",
         corner=1.15, bevel=1.30, plate=1.35)
    + [
        # brow, raked forward a touch so the front edge is not a flat wall
        tilted("Head", "brow", [-4.10, 25.75, -4.55], [8.20, 1.00, 1.45], "shell_black",
               rot=[-7.5, 0, 0]),
        tilted("Head", "brow_lip", [-3.55, 25.35, -4.75], [7.10, 0.55, 1.05], "hardware",
               rot=[-12, 0, 0]),
        # occipital shelf, tilted back
        tilted("Head", "nape", [-4.15, 25.00, 1.55], [8.30, 1.60, 2.85], "shell_black",
               rot=[10, 0, 0]),
        plain("Head", "nape_pad", [-3.40, 24.35, 2.30], [6.80, 1.00, 1.60], "webbing_dark"),

        # --- NVG shroud: raked plate, three-lug block, side wings
        tilted("Head", "shroud_base", [-1.95, 29.00, -4.75], [3.90, 2.10, 0.60], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_lug", [-0.80, 29.55, -5.15], [1.60, 1.05, 0.55], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_wing_r", [-2.85, 29.35, -4.65], [0.95, 1.15, 0.50], "hardware",
               rot=[-14, 0, -9]),
        tilted("Head", "shroud_wing_l", [1.90, 29.35, -4.65], [0.95, 1.15, 0.50], "hardware",
               rot=[-14, 0, 9]),

        # --- ARC rails, angled to follow the shell taper
        tilted("Head", "rail_r", [-4.70, 26.95, -2.85], [0.55, 1.00, 4.80], "hardware",
               rot=[0, 0, 6]),
        tilted("Head", "rail_l", [4.15, 26.95, -2.85], [0.55, 1.00, 4.80], "hardware",
               rot=[0, 0, -6]),
        plain("Head", "rail_clip_r", [-4.90, 27.20, -1.15], [0.35, 0.65, 1.50], "hardware"),
        plain("Head", "rail_clip_l", [4.55, 27.20, -1.15], [0.35, 0.65, 1.50], "hardware"),

        # --- mandible guard: arms sweep in, mesh face plate rakes back
        tilted("Head", "mand_arm_r", [-4.55, 24.30, -3.85], [0.80, 2.70, 3.25], "hardware",
               rot=[0, 0, -8]),
        tilted("Head", "mand_arm_l", [3.75, 24.30, -3.85], [0.80, 2.70, 3.25], "hardware",
               rot=[0, 0, 8]),
        tilted("Head", "mand_face", [-3.40, 24.05, -4.85], [6.80, 2.65, 0.95], "mesh",
               rot=[9, 0, 0]),
        tilted("Head", "mand_lip", [-3.50, 26.35, -4.95], [7.00, 0.65, 1.15], "hardware",
               rot=[-16, 0, 0]),
        tilted("Head", "mand_chin", [-2.75, 23.35, -4.55], [5.50, 0.80, 3.45], "shell_black",
               rot=[16, 0, 0]),

        # --- installable NVGs on their own bone: hidden unless a set of
        # goggles is fitted, and rotated up by the nvg_up animation.
        plain("nvg", "nvg_arm", [-0.55, 29.55, -5.75], [1.10, 0.55, 1.70], "hardware"),
        tilted("nvg", "nvg_bridge", [-1.95, 28.55, -6.30], [3.90, 0.95, 0.95], "hardware",
               rot=[-6, 0, 0]),
        plain("nvg", "nvg_tube_r", [-1.90, 27.35, -6.75], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_tube_l", [0.35, 27.35, -6.75], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_lens_r", [-1.75, 27.50, -7.00], [1.25, 1.25, 0.35], "glass_tint"),
        plain("nvg", "nvg_lens_l", [0.50, 27.50, -7.00], [1.25, 1.25, 0.35], "glass_tint"),

        # --- retention straps, splayed
        tilted("Head", "strap_r", [-4.45, 24.10, -1.30], [0.45, 2.20, 2.75], "webbing_dark",
               rot=[0, 0, -5]),
        tilted("Head", "strap_l", [4.00, 24.10, -1.30], [0.45, 2.20, 2.75], "webbing_dark",
               rot=[0, 0, 5]),
    ]
)

# ------------------------------------------------------------------- zsh ----
# Tall rounded dome, so the octagon gets a bigger corner cut and the crown a
# deeper chamfer than the other two.
ZSH = (
    dome("Head", "dome", -4.30, 4.30, -4.30, 4.30, 26.10, 32.35, "olive",
         corner=1.30, bevel=1.55, plate=1.50)
    + [
        # raised brow band, slightly proud of the shell all the way round
        plain("Head", "band_x", [-4.42, 26.00, -3.15], [8.84, 0.80, 6.30], "olive_dark"),
        plain("Head", "band_z", [-3.15, 26.00, -4.42], [6.30, 0.80, 8.84], "olive_dark"),
    ]
    + corner_posts("Head", "band", -4.42, 4.42, -4.42, 4.42, 26.00, 0.80, 1.30, 1.35,
                   "olive_dark")
    + [
        # the distinctive front lip, flared forward and down
        tilted("Head", "lip", [-3.40, 23.55, -4.95], [6.80, 2.35, 0.70], "olive",
               rot=[14, 0, 0]),
        tilted("Head", "lip_edge", [-3.55, 23.25, -5.05], [7.10, 0.45, 0.80], "olive_dark",
               rot=[14, 0, 0]),

        tilted("Head", "mount_r", [-5.05, 26.05, -0.75], [0.95, 1.80, 2.45], "hardware",
               rot=[0, 0, 5]),
        tilted("Head", "mount_l", [4.10, 26.05, -0.75], [0.95, 1.80, 2.45], "hardware",
               rot=[0, 0, -5]),
        plain("Head", "mount_clip_l", [5.00, 26.45, -0.35], [0.45, 0.95, 1.40], "hardware"),
        plain("Head", "top_stud", [-0.35, 32.30, -1.35], [0.70, 0.55, 0.70], "hardware"),

        tilted("Head", "nape", [-4.10, 24.95, 1.70], [8.20, 1.40, 2.75], "olive_dark",
               rot=[12, 0, 0]),
        plain("Head", "chin_cup", [-2.45, 22.65, -3.50], [4.90, 1.30, 4.20], "webbing_dark"),

        # ---- flip-up visor assembly on the "visor" bone.
        # Hinge pivot [0, 26.9, -4.2]; helmet_open rotates this bone -50 on X.
        # Cube-level tilts here compose with that bone rotation.
        tilted("visor", "v_frame", [-3.95, 24.05, -5.75], [7.90, 3.05, 0.95], "hardware",
               rot=[7, 0, 0]),
        tilted("visor", "v_glass", [-3.35, 24.45, -6.05], [6.70, 2.10, 0.45], "glass_tint",
               rot=[7, 0, 0]),
        tilted("visor", "v_hood", [-4.00, 26.95, -5.85], [8.00, 0.60, 1.75], "hardware",
               rot=[-18, 0, 0]),
        tilted("visor", "v_arm_r", [-4.35, 24.45, -5.00], [0.60, 2.60, 2.00], "hardware",
               rot=[0, 0, -6]),
        tilted("visor", "v_arm_l", [3.75, 24.45, -5.00], [0.60, 2.60, 2.00], "hardware",
               rot=[0, 0, 6]),
    ]
)

# ---------------------------------------------------------- peacekeeper -----
PEACEKEEPER = (
    dome("Head", "shell", -4.35, 4.35, -4.35, 4.35, 25.95, 32.05, "un_blue",
         corner=1.20, bevel=1.40, plate=1.40)
    + [
        # all-round brim: two flats plus rotated corner posts, each edge tipped
        # slightly downward so the rim reads as a curve rather than a shelf
        tilted("Head", "brim_n", [-4.30, 25.35, -5.05], [8.60, 0.85, 1.25], "un_blue_dark",
               rot=[-9, 0, 0]),
        tilted("Head", "brim_s", [-4.30, 25.35, 3.80], [8.60, 0.85, 1.25], "un_blue_dark",
               rot=[9, 0, 0]),
        tilted("Head", "brim_e", [3.80, 25.35, -4.30], [1.25, 0.85, 8.60], "un_blue_dark",
               rot=[0, 0, -9]),
        tilted("Head", "brim_w", [-5.05, 25.35, -4.30], [1.25, 0.85, 8.60], "un_blue_dark",
               rot=[0, 0, 9]),
    ]
    + corner_posts("Head", "brim", -4.85, 4.85, -4.85, 4.85, 25.35, 0.85, 1.45, 1.50,
                   "un_blue_dark")
    + [
        # front panel carries the insignia
        tilted("Head", "front_panel", [-2.60, 27.60, -4.62], [5.20, 3.00, 0.32], "un_blue",
               rot=[-4, 0, 0],
               decal={"face": "north", "type": "roundel", "color": (206, 214, 222)}),

        plain("Head", "bolt_r", [-4.72, 27.65, -1.30], [0.33, 0.55, 0.55], "hardware"),
        plain("Head", "bolt_l", [4.39, 27.65, -1.30], [0.33, 0.55, 0.55], "hardware"),

        # hanging retention straps, angled outward off the shell
        tilted("Head", "strap_rf", [-4.60, 22.30, -2.80], [0.45, 3.20, 0.95], "webbing",
               rot=[0, 0, -4]),
        tilted("Head", "strap_rb", [-4.60, 22.80, 0.75], [0.45, 2.70, 0.95], "webbing",
               rot=[0, 0, -4]),
        tilted("Head", "strap_lf", [4.15, 22.30, -2.80], [0.45, 3.20, 0.95], "webbing",
               rot=[0, 0, 4]),
        tilted("Head", "strap_lb", [4.15, 22.80, 0.75], [0.45, 2.70, 0.95], "webbing",
               rot=[0, 0, 4]),
        plain("Head", "strap_join_r", [-4.60, 22.25, -1.95], [0.45, 0.55, 2.80], "webbing"),
        plain("Head", "strap_join_l", [4.15, 22.25, -1.95], [0.45, 0.55, 2.80], "webbing"),
        tilted("Head", "chin_cup", [-1.75, 21.85, -3.35], [3.50, 1.05, 1.40], "webbing",
               rot=[14, 0, 0]),
    ]
)

HELMET_MODELS = {
    "bastion":     (BASTION, 128, 91101,
                    [("Head", "armorHead", [0, 24, 0]),
                     ("nvg", "Head", [0, 29.6, -5.0])]),
    "zsh":         (ZSH, 128, 91102,
                    [("Head", "armorHead", [0, 24, 0]),
                     ("visor", "Head", [0, 26.9, -4.2])]),
    "peacekeeper": (PEACEKEEPER, 128, 91103,
                    [("Head", "armorHead", [0, 24, 0])]),
}

# Goggles stow upward about the shroud pivot. The bone is hidden entirely when
# no goggles are installed, so one model covers both states.
BASTION_ANIMATION = {
    "format_version": "1.8.0",
    "animations": {
        "nvg_down": {
            "loop": "hold_on_last_frame",
            "animation_length": 0.4,
            "bones": {"nvg": {"rotation": {
                "0.0": {"vector": [-78, 0, 0]},
                "0.15": {"vector": [-10, 0, 0]},
                "0.28": {"vector": [4, 0, 0]},
                "0.4": {"vector": [0, 0, 0]},
            }}},
        },
        "nvg_up": {
            "loop": "hold_on_last_frame",
            "animation_length": 0.4,
            "bones": {"nvg": {"rotation": {
                "0.0": {"vector": [0, 0, 0]},
                "0.15": {"vector": [-82, 0, 0]},
                "0.28": {"vector": [-74, 0, 0]},
                "0.4": {"vector": [-78, 0, 0]},
            }}},
        },
    },
}

# Flip-visor animation, matching the killa/tagilla pattern the mod already uses.
ZSH_ANIMATION = {
    "format_version": "1.8.0",
    "animations": {
        "helmet_open": {
            "loop": "hold_on_last_frame",
            "animation_length": 0.5,
            "bones": {"visor": {"rotation": {
                "0.0": {"vector": [0, 0, 0]},
                "0.1": {"vector": [-52, 0, 0]},
                "0.25": {"vector": [-46, 0, 0]},
                "0.4": {"vector": [-52, 0, 0]},
                "0.5": {"vector": [-50, 0, 0]},
            }}},
        },
        "helmet_closed": {
            "loop": "hold_on_last_frame",
            "animation_length": 0.5,
            "bones": {"visor": {"rotation": {
                "0.0": {"vector": [-50, 0, 0]},
                "0.1": {"vector": [-12, 0, 0]},
                "0.25": {"vector": [5, 0, 0]},
                "0.4": {"vector": [-2, 0, 0]},
                "0.5": {"vector": [0, 0, 0]},
            }}},
        },
    },
}
