#!/usr/bin/env python3
"""The three helmets.

Shells are rounded domes built from stacked octagonal rings (see geom.dome);
fittings carry small deliberate tilts.

  bastion  - black high-cut shell, NVG shroud, ARC rails, mesh mandible
  k63      - olive dome, brow band, front lip, flip-up tinted visor
  untar    - blue dome with an all-round brim and short chin straps

Head cube spans y 24..32, x/z -4..4. The eyes sit at roughly y 28, so a shell
that starts below about y 27 covers the face — every piece here is positioned
against that line.
"""

from geom import dome, plain, tilted, corner_posts

# --------------------------------------------------------------- bastion ----
BASTION = (
    dome("Head", "shell", -4.25, 4.25, -4.25, 4.25, 27.30, 32.45, "shell_black",
         rings=8, corner=1.15)
    + [
        # brow, raked forward so the front edge is not a flat wall
        tilted("Head", "brow", [-4.05, 27.00, -4.55], [8.10, 0.95, 1.35], "shell_black",
               rot=[-7.5, 0, 0]),
        tilted("Head", "brow_lip", [-3.50, 26.70, -4.70], [7.00, 0.50, 1.00], "hardware",
               rot=[-12, 0, 0]),
        # occipital shelf
        tilted("Head", "nape", [-4.00, 26.60, 1.60], [8.00, 1.55, 2.70], "shell_black",
               rot=[10, 0, 0]),
        plain("Head", "nape_pad", [-3.30, 26.05, 2.30], [6.60, 0.95, 1.50], "webbing_dark"),

        # --- NVG shroud on the front of the crown
        tilted("Head", "shroud_base", [-1.95, 29.85, -4.45], [3.90, 2.00, 0.60], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_lug", [-0.80, 30.35, -4.85], [1.60, 1.00, 0.55], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_wing_r", [-2.80, 30.15, -4.35], [0.90, 1.10, 0.50], "hardware",
               rot=[-14, 0, -9]),
        tilted("Head", "shroud_wing_l", [1.90, 30.15, -4.35], [0.90, 1.10, 0.50], "hardware",
               rot=[-14, 0, 9]),

        # --- ARC rails down each side
        tilted("Head", "rail_r", [-4.45, 27.95, -2.70], [0.55, 0.95, 4.50], "hardware",
               rot=[0, 0, 6]),
        tilted("Head", "rail_l", [3.90, 27.95, -2.70], [0.55, 0.95, 4.50], "hardware",
               rot=[0, 0, -6]),
        plain("Head", "rail_clip_r", [-4.65, 28.20, -1.10], [0.35, 0.60, 1.40], "hardware"),
        plain("Head", "rail_clip_l", [4.30, 28.20, -1.10], [0.35, 0.60, 1.40], "hardware"),

        # --- mandible guard over the jaw, meeting the shell at the brow line
        tilted("Head", "mand_arm_r", [-4.45, 24.60, -3.80], [0.75, 2.65, 3.10], "hardware",
               rot=[0, 0, -8]),
        tilted("Head", "mand_arm_l", [3.70, 24.60, -3.80], [0.75, 2.65, 3.10], "hardware",
               rot=[0, 0, 8]),
        tilted("Head", "mand_face", [-3.35, 24.40, -4.80], [6.70, 2.60, 0.90], "mesh",
               rot=[9, 0, 0]),
        tilted("Head", "mand_lip", [-3.45, 26.70, -4.85], [6.90, 0.60, 1.10], "hardware",
               rot=[-16, 0, 0]),
        tilted("Head", "mand_chin", [-2.70, 23.85, -4.45], [5.40, 0.75, 3.35], "shell_black",
               rot=[16, 0, 0]),

        # --- installable NVGs on their own bone: hidden unless goggles are
        # fitted, rotated up by the nvg_up animation. Lowered, they sit in
        # front of the eyes at about y 28.
        plain("nvg", "nvg_arm", [-0.55, 29.60, -5.60], [1.10, 0.55, 1.80], "hardware"),
        tilted("nvg", "nvg_bridge", [-1.95, 28.55, -6.15], [3.90, 0.95, 0.95], "hardware",
               rot=[-6, 0, 0]),
        plain("nvg", "nvg_tube_r", [-1.90, 27.30, -6.60], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_tube_l", [0.35, 27.30, -6.60], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_lens_r", [-1.75, 27.45, -6.85], [1.25, 1.25, 0.35], "glass_tint"),
        plain("nvg", "nvg_lens_l", [0.50, 27.45, -6.85], [1.25, 1.25, 0.35], "glass_tint"),

        # --- retention straps, short and hugging the sides of the jaw
        tilted("Head", "strap_r", [-4.30, 25.60, -1.30], [0.45, 1.90, 2.60], "webbing_dark",
               rot=[0, 0, -5]),
        tilted("Head", "strap_l", [3.85, 25.60, -1.30], [0.45, 1.90, 2.60], "webbing_dark",
               rot=[0, 0, 5]),
    ]
)

# ------------------------------------------------------------------- k63 ----
K63 = (
    dome("Head", "dome", -4.30, 4.30, -4.30, 4.30, 27.10, 32.70, "olive",
         rings=8, corner=1.30)
    + [
        # raised brow band, proud of the shell all the way round
        plain("Head", "band_x", [-4.44, 27.00, -3.10], [8.88, 0.85, 6.20], "olive_dark"),
        plain("Head", "band_z", [-3.10, 27.00, -4.44], [6.20, 0.85, 8.88], "olive_dark"),
    ]
    + corner_posts("Head", "band", -4.44, 4.44, -4.44, 4.44, 27.00, 0.85, 1.30, 1.35,
                   "olive_dark")
    + [
        # the distinctive front lip, flared forward and down over the brow
        tilted("Head", "lip", [-3.40, 25.95, -4.95], [6.80, 1.85, 0.70], "olive",
               rot=[14, 0, 0]),
        tilted("Head", "lip_edge", [-3.55, 25.70, -5.05], [7.10, 0.45, 0.80], "olive_dark",
               rot=[14, 0, 0]),

        tilted("Head", "mount_r", [-4.85, 27.85, -0.75], [0.90, 1.60, 2.35], "hardware",
               rot=[0, 0, 5]),
        tilted("Head", "mount_l", [3.95, 27.85, -0.75], [0.90, 1.60, 2.35], "hardware",
               rot=[0, 0, -5]),
        plain("Head", "mount_clip_l", [4.80, 28.20, -0.35], [0.45, 0.90, 1.35], "hardware"),
        plain("Head", "top_stud", [-0.35, 32.60, -1.30], [0.70, 0.55, 0.70], "hardware"),

        tilted("Head", "nape", [-4.00, 26.55, 1.70], [8.00, 1.30, 2.60], "olive_dark",
               rot=[12, 0, 0]),
        plain("Head", "chin_cup", [-2.35, 24.15, -3.30], [4.70, 1.15, 3.90], "webbing_dark"),

        # ---- flip-up visor assembly on the "visor" bone.
        # Hinge pivot [0, 27.9, -4.2]; helmet_open rotates this bone -50 on X.
        tilted("visor", "v_frame", [-3.90, 24.80, -5.65], [7.80, 2.95, 0.90], "hardware",
               rot=[7, 0, 0]),
        tilted("visor", "v_glass", [-3.30, 25.20, -5.95], [6.60, 2.05, 0.45], "glass_tint",
               rot=[7, 0, 0]),
        tilted("visor", "v_hood", [-3.95, 27.55, -5.75], [7.90, 0.60, 1.70], "hardware",
               rot=[-18, 0, 0]),
        tilted("visor", "v_arm_r", [-4.30, 25.20, -4.95], [0.60, 2.55, 1.95], "hardware",
               rot=[0, 0, -6]),
        tilted("visor", "v_arm_l", [3.70, 25.20, -4.95], [0.60, 2.55, 1.95], "hardware",
               rot=[0, 0, 6]),
    ]
)

# ----------------------------------------------------------------- untar ----
UNTAR = (
    dome("Head", "shell", -4.35, 4.35, -4.35, 4.35, 27.15, 32.35, "un_blue",
         rings=8, corner=1.20)
    + [
        # all-round brim, each edge tipped slightly downward so the rim reads
        # as a curve rather than a shelf
        tilted("Head", "brim_n", [-4.20, 26.95, -4.72], [8.40, 0.78, 1.05], "un_blue_dark",
               rot=[-9, 0, 0]),
        tilted("Head", "brim_s", [-4.20, 26.95, 3.67], [8.40, 0.78, 1.05], "un_blue_dark",
               rot=[9, 0, 0]),
        tilted("Head", "brim_e", [3.67, 26.95, -4.20], [1.05, 0.78, 8.40], "un_blue_dark",
               rot=[0, 0, -9]),
        tilted("Head", "brim_w", [-4.72, 26.95, -4.20], [1.05, 0.78, 8.40], "un_blue_dark",
               rot=[0, 0, 9]),
    ]
    + corner_posts("Head", "brim", -4.60, 4.60, -4.60, 4.60, 26.95, 0.78, 1.35, 1.40,
                   "un_blue_dark")
    + [
        # front panel carries the insignia
        tilted("Head", "front_panel", [-2.55, 28.70, -4.50], [5.10, 2.90, 0.32], "un_blue",
               rot=[-4, 0, 0],
               decal={"face": "north", "type": "roundel", "color": (206, 214, 222)}),

        plain("Head", "bolt_r", [-4.45, 28.55, -1.30], [0.33, 0.55, 0.55], "hardware"),
        plain("Head", "bolt_l", [4.12, 28.55, -1.30], [0.33, 0.55, 0.55], "hardware"),

        # short chin straps down the sides of the jaw to a cup under the chin
        tilted("Head", "strap_rf", [-4.35, 25.10, -2.30], [0.42, 2.00, 0.90], "webbing",
               rot=[0, 0, -4]),
        tilted("Head", "strap_rb", [-4.35, 25.40, 0.60], [0.42, 1.70, 0.90], "webbing",
               rot=[0, 0, -4]),
        tilted("Head", "strap_lf", [3.93, 25.10, -2.30], [0.42, 2.00, 0.90], "webbing",
               rot=[0, 0, 4]),
        tilted("Head", "strap_lb", [3.93, 25.40, 0.60], [0.42, 1.70, 0.90], "webbing",
               rot=[0, 0, 4]),
        plain("Head", "chin_cup", [-2.10, 24.45, -2.60], [4.20, 0.85, 4.20], "webbing"),
    ]
)

HELMET_MODELS = {
    "bastion": (BASTION, 128, 91101,
                [("Head", "armorHead", [0, 24, 0]),
                 ("nvg", "Head", [0, 30.0, -4.3])]),
    "k63":     (K63, 128, 91102,
                [("Head", "armorHead", [0, 24, 0]),
                 ("visor", "Head", [0, 27.9, -4.2])]),
    "untar":   (UNTAR, 128, 91103,
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

# Flip-visor animation, matching the killa/tagilla pattern Fracture Point uses.
K63_ANIMATION = {
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
