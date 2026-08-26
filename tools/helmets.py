#!/usr/bin/env python3
"""The three helmets.

Shells are faceted domes (see geom.dome): octagonal in plan, tapering as they
rise, with a two-step chamfered crown whose four corners are closed by sloping
facets rather than vertical fillers.

  bastion  - black high-cut shell, open face, NVG shroud, ARC rails,
               rear dial, counterweight, four-point chinstrap
  k63      - olive dome, brow band, front lip, flip-up tinted visor over a
               fixed jaw plate
  untar    - blue dome, all-round brim, cover seams, four-point chinstrap

Head cube spans y 24..32, x/z -4..4. Three constraints, and they fight:

  brow  ~ y 28.35      the eyes sit at about y 28, so a rim below that covers
                       the face. This is the floor, not a target: everything
                       hung under the shell — brow, band, lip, brim — has to
                       clear it too, or the helmet still reads as too low
  crown ~ y 33.2-33.4  worn high with the top cut back, about 1.3 above the
                       skull. Taller reads as a dome swallowing the head
  width   2*W - c >= 8 the head is an 8-wide BOX. Cutting the octagon's corners
                       by c pulls the shell inside the head's own corners
                       unless the footprint is wide enough to pay for it, and
                       then the player's skin shows through at 45 degrees

The third one is why these shells are ~9.2 wide rather than the ~8.5 the source
mod's look suggests: 9.2 is also what vanilla's own helmet layer uses, for the
same reason.

It also rules out a taper below y 32 — an inset anywhere over the skull uncovers
it all the way round — so the wall runs straight to the top of the head and all
the rounding lives in the crown above it. `fit_check.py` asserts this at 16
azimuths; run it after moving anything.

Judge all of this at GAME scale, not preview scale. A helmet is about 30 pixels
on a player's head; `fit_check.py` renders at 430 for detail, which flatters
everything. A crown chamfer that reads as a dome at 400 pixels is a plateau at
30, and a facet poking half a unit past the shell is invisible in a big render
and the most obvious thing about the helmet in game. `preview/worn_game_scale.png`
is rendered at the size the game draws — check there before believing anything.

The same 8-cube rules the trim. Anything hung on the shell has to clear the head
to be drawn at all: side hardware past |x| 4.0, brow and chin work forward of
z -4.0, seams above the crown it sits on. A detail tucked "under the jaw" is
simply inside the head and invisible, which is why the chinstraps run down the
outside of the jaw and close across the front of the chin rather than beneath it.
"""

from geom import dome, plain, tilted, corner_posts, chinstrap

# --------------------------------------------------------------- bastion ----
BASTION = (
    dome("Head", "shell", -4.66, 4.66, -4.66, 4.66, 28.40, 33.40, "shell_black",
         corner=1.10, bevel=1.40, plate=1.35, taper=0.0, flare=1.55)
    + [
        # brow, raked forward so the front edge is not a flat wall
        tilted("Head", "brow", [-4.40, 28.10, -4.95], [8.80, 0.95, 1.35], "shell_black",
               rot=[-7.5, 0, 0]),
        tilted("Head", "brow_lip", [-3.60, 27.85, -5.08], [7.20, 0.50, 1.00], "hardware",
               rot=[-12, 0, 0]),
        # occipital shelf
        tilted("Head", "nape", [-4.35, 27.70, 1.95], [8.70, 1.55, 2.95], "shell_black",
               rot=[10, 0, 0]),
        plain("Head", "nape_pad", [-3.55, 27.20, 3.05], [7.10, 0.95, 1.80], "webbing_dark"),

        # --- NVG shroud on the front of the crown
        tilted("Head", "shroud_base", [-1.95, 29.85, -4.98], [3.90, 1.85, 0.62], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_lug", [-0.80, 30.35, -5.38], [1.60, 0.95, 0.58], "hardware",
               rot=[-14, 0, 0]),
        tilted("Head", "shroud_wing_r", [-2.85, 30.10, -4.88], [0.95, 1.05, 0.52], "hardware",
               rot=[-14, 0, -9]),
        tilted("Head", "shroud_wing_l", [1.90, 30.10, -4.88], [0.95, 1.05, 0.52], "hardware",
               rot=[-14, 0, 9]),

        # --- ARC rails down each side
        tilted("Head", "rail_r", [-4.88, 28.60, -2.70], [0.60, 0.95, 4.50], "hardware",
               rot=[0, 0, 6]),
        tilted("Head", "rail_l", [4.28, 28.60, -2.70], [0.60, 0.95, 4.50], "hardware",
               rot=[0, 0, -6]),
        plain("Head", "rail_clip_r", [-5.10, 28.85, -1.10], [0.38, 0.60, 1.40], "hardware"),
        plain("Head", "rail_clip_l", [4.72, 28.85, -1.10], [0.38, 0.60, 1.40], "hardware"),

        # No mandible guard. There was a mesh one over the jaw; it sat across
        # the player's face and there is no way to keep a face guard that does
        # not. This is a high-cut shell with an open face.

        # --- installable NVGs on their own bone: hidden unless goggles are
        # fitted, rotated up by the nvg_up animation. Lowered, they sit in
        # front of the eyes at about y 28.
        plain("nvg", "nvg_arm", [-0.55, 29.10, -5.55], [1.10, 2.70, 1.30], "hardware"),
        tilted("nvg", "nvg_bridge", [-1.95, 28.55, -6.15], [3.90, 0.95, 0.95], "hardware",
               rot=[-6, 0, 0]),
        plain("nvg", "nvg_tube_r", [-1.90, 27.30, -6.60], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_tube_l", [0.35, 27.30, -6.60], [1.55, 1.55, 2.45], "hardware"),
        plain("nvg", "nvg_lens_r", [-1.75, 27.45, -6.85], [1.25, 1.25, 0.35], "glass_tint"),
        plain("nvg", "nvg_lens_l", [0.50, 27.45, -6.85], [1.25, 1.25, 0.35], "glass_tint"),

        # --- rear retention dial, canted back with the occipital shelf
        tilted("Head", "dial_base", [-1.20, 28.75, 4.05], [2.40, 2.40, 0.85], "hardware",
               rot=[15, 0, 0]),
        tilted("Head", "dial_knob", [-0.72, 29.20, 4.62], [1.44, 1.44, 0.62], "webbing_dark",
               rot=[15, 0, 0]),

        # --- counterweight pouch, sitting back on the slope of the crown
        tilted("Head", "cw_pouch", [-1.85, 30.20, 3.05], [3.70, 1.70, 1.15], "webbing_dark",
               rot=[26, 0, 0]),
        tilted("Head", "cw_strap", [-2.05, 31.30, 1.55], [4.10, 0.42, 2.30], "webbing_dark",
               rot=[6, 0, 0]),

        # --- loop panels down each side, following the rail line
        tilted("Head", "velcro_r", [-4.82, 29.35, -0.40], [0.32, 1.75, 2.45], "webbing_dark",
               rot=[0, 0, 7]),
        tilted("Head", "velcro_l", [4.50, 29.35, -0.40], [0.32, 1.75, 2.45], "webbing_dark",
               rot=[0, 0, -7]),

        # --- IR strobe clipped to the left rail. Three axes: it follows the
        # rail's cant, angles outward, and noses up.
        tilted("Head", "strobe", [4.62, 29.85, 1.15], [0.72, 0.82, 1.25], "hardware",
               rot=[9, 14, -7]),
        tilted("Head", "strobe_lens", [4.70, 30.62, 1.35], [0.52, 0.22, 0.85], "glass_tint",
               rot=[9, 14, -7]),

        # --- swept side trim. The high-cut sweep over the ear is the shape
        # this helmet is known for and a straight strip cannot suggest it;
        # these run on three axes so the line rises toward the back.
        tilted("Head", "swept_r", [-4.86, 28.50, -1.70], [0.38, 0.95, 4.30], "hardware",
               rot=[-7, 11, 8]),
        tilted("Head", "swept_l", [4.48, 28.50, -1.70], [0.38, 0.95, 4.30], "hardware",
               rot=[-7, -11, -8]),

        # --- crown seam, canted forward with the fall of the crown
        tilted("Head", "seam", [-0.50, 33.06, -1.85], [1.00, 0.40, 3.70], "hardware",
               rot=[6, 0, 0]),

        # --- raked peak over the brow
        tilted("Head", "peak", [-2.65, 28.90, -5.20], [5.30, 0.52, 1.15], "shell_black",
               rot=[-27, 0, 0]),

        # --- brow bolts, raked with the brow they sit on
        tilted("Head", "bolt_r", [-3.35, 28.55, -5.04], [0.58, 0.58, 0.48], "hardware",
               rot=[-7.5, 0, 0]),
        tilted("Head", "bolt_l", [2.77, 28.55, -5.04], [0.58, 0.58, 0.48], "hardware",
               rot=[-7.5, 0, 0]),
    ]
    # four-point retention, leaning in to a cup under the chin
    + chinstrap("Head", "strap", 4.56, 28.20, 24.95, "webbing_dark", "hardware",
                z_front=-2.75, z_back=0.75, width=0.54, splay=5.0,
                front_rake=7.0, back_rake=9.0,
                cup_z=-2.95, cup=(7.80, 0.84, 0.0))
)

# ------------------------------------------------------------------- k63 ----
K63 = (
    # Worn high with the top cut back, per the hand-edited side view: rim at
    # 28.35 so the eyes (about y 28) stay clear, crown down at 33.20. The wall
    # runs straight to the top of the head and the two-step crown does all the
    # rounding — see the module docstring for why a taper cannot go below y 32.
    dome("Head", "dome", -4.68, 4.68, -4.68, 4.68, 28.35, 33.20, "olive",
         corner=1.12, bevel=1.20, plate=1.50, taper=0.0, flare=1.70)
    + [
        # raised brow band, proud of the shell all the way round
        plain("Head", "band_x", [-4.84, 28.05, -3.30], [9.68, 0.85, 6.60], "olive_dark"),
        plain("Head", "band_z", [-3.30, 28.05, -4.84], [6.60, 0.85, 9.68], "olive_dark"),
    ]
    + corner_posts("Head", "band", -4.84, 4.84, -4.84, 4.84, 28.05, 0.85, 1.38, 1.40,
                   "olive_dark")
    + [
        # the distinctive front lip, flared forward and down over the brow
        tilted("Head", "lip", [-3.60, 27.90, -5.18], [7.20, 1.55, 0.72], "olive",
               rot=[14, 0, 0]),
        tilted("Head", "lip_edge", [-3.75, 27.65, -5.30], [7.50, 0.45, 0.82], "olive_dark",
               rot=[14, 0, 0]),

        tilted("Head", "mount_r", [-5.18, 28.75, -0.75], [0.92, 1.60, 2.35], "hardware",
               rot=[0, 0, 5]),
        tilted("Head", "mount_l", [4.26, 28.75, -0.75], [0.92, 1.60, 2.35], "hardware",
               rot=[0, 0, -5]),
        plain("Head", "mount_clip_l", [5.14, 29.10, -0.35], [0.46, 0.90, 1.35], "hardware"),
        plain("Head", "top_stud", [-0.35, 33.12, -1.20], [0.70, 0.50, 0.70], "hardware"),

        tilted("Head", "nape", [-4.38, 27.65, 2.05], [8.76, 1.30, 2.90], "olive_dark",
               rot=[12, 0, 0]),

        # comms box on the right shell, canted out and back off two axes
        tilted("Head", "comms", [-4.90, 29.20, 1.55], [0.55, 1.15, 1.30], "hardware",
               rot=[0, -12, 7]),
        tilted("Head", "comms_cap", [-5.02, 29.68, 1.80], [0.24, 0.48, 0.66], "webbing_dark",
               rot=[0, -12, 7]),

        # crown seam, tipped forward so it follows the fall of the crown
        tilted("Head", "seam", [-0.48, 32.90, -1.75], [0.96, 0.40, 3.50], "olive_dark",
               rot=[5, 0, 0]),

        # swept trim along the lower shell, rising toward the back
        tilted("Head", "swept_r", [-4.88, 29.05, -1.55], [0.36, 0.85, 4.10], "olive_dark",
               rot=[-6, 10, 7]),
        tilted("Head", "swept_l", [4.52, 29.05, -1.55], [0.36, 0.85, 4.10], "olive_dark",
               rot=[-6, -10, -7]),

        # rear adjuster block, raked with the nape
        tilted("Head", "adjuster", [-1.65, 29.05, 4.30], [3.30, 1.25, 0.72], "hardware",
               rot=[13, 0, 0]),

        # band rivets, each tipped to sit flat on the band it rides
        tilted("Head", "rivet_rf", [-4.02, 28.28, -5.02], [0.42, 0.42, 0.34], "hardware",
               rot=[0, 0, 6]),
        tilted("Head", "rivet_lf", [3.60, 28.28, -5.02], [0.42, 0.42, 0.34], "hardware",
               rot=[0, 0, -6]),
        tilted("Head", "rivet_r", [-5.02, 28.28, -0.21], [0.34, 0.42, 0.42], "hardware",
               rot=[6, 0, 0]),
        tilted("Head", "rivet_l", [4.68, 28.28, -0.21], [0.34, 0.42, 0.42], "hardware",
               rot=[-6, 0, 0]),

        # visor hinge plates, splayed off the shell
        tilted("Head", "hinge_r", [-4.95, 28.55, -3.70], [0.62, 1.15, 1.55], "hardware",
               rot=[-8, 0, 8]),
        tilted("Head", "hinge_l", [4.33, 28.55, -3.70], [0.62, 1.15, 1.55], "hardware",
               rot=[-8, 0, -8]),

        plain("Head", "chin_cup", [-2.35, 24.55, -3.30], [4.70, 1.15, 3.90], "webbing_dark"),

        # ---- fixed lower faceplate.
        # This is on the *Head* bone, not the visor, which is the whole point:
        # it is the second layer, armour over the mouth and jaw that stays put
        # when the visor lifts. Shell-coloured, because it is part of the shell.
        # It has to live forward of z -4.0 to be drawn at all, and it flares as
        # it drops so the jaw line is a rake rather than a flat wall.
        tilted("Head", "face_plate", [-4.10, 24.35, -5.28], [8.20, 2.30, 0.80], "olive",
               rot=[17, 0, 0]),
        tilted("Head", "face_lip", [-4.22, 24.00, -5.44], [8.44, 0.58, 0.94], "olive_dark",
               rot=[17, 0, 0]),
        # louvre slot across the plate, raked with it
        tilted("Head", "face_slot", [-2.70, 25.95, -5.52], [5.40, 0.40, 0.55], "hardware",
               rot=[17, 0, 0]),
        # cheek returns, wrapping the plate back toward the jaw on two axes
        tilted("Head", "face_cheek_r", [-4.52, 24.70, -4.95], [0.74, 2.10, 1.45], "olive",
               rot=[6, 15, 7]),
        tilted("Head", "face_cheek_l", [3.78, 24.70, -4.95], [0.74, 2.10, 1.45], "olive",
               rot=[6, -15, -7]),
        # side plates carrying the armour back over the ear to meet the nape.
        # The plate is not a front panel: it wraps, so the helmet reads as
        # closed from every angle rather than only head-on. Tapered inward at
        # the bottom to follow the jaw.
        tilted("Head", "face_side_r", [-4.66, 25.20, -3.70], [0.80, 3.10, 5.00], "olive",
               rot=[-4, 0, 6]),
        tilted("Head", "face_side_l", [3.86, 25.20, -3.70], [0.80, 3.10, 5.00], "olive",
               rot=[-4, 0, -6]),
        tilted("Head", "face_side_lip_r", [-4.80, 24.92, -3.55], [0.90, 0.58, 4.70], "olive_dark",
               rot=[-4, 0, 6]),
        tilted("Head", "face_side_lip_l", [3.90, 24.92, -3.55], [0.90, 0.58, 4.70], "olive_dark",
               rot=[-4, 0, -6]),
        # arms carrying the plate up to the shell, inboard of the visor arms
        tilted("Head", "face_arm_r", [-4.48, 26.15, -4.60], [0.62, 2.30, 1.60], "olive",
               rot=[-7, 0, 5]),
        tilted("Head", "face_arm_l", [3.86, 26.15, -4.60], [0.62, 2.30, 1.60], "olive",
               rot=[-7, 0, -5]),
        # bolts where the arms meet the plate
        tilted("Head", "face_bolt_r", [-4.62, 26.05, -4.62], [0.44, 0.44, 0.38], "hardware",
               rot=[0, 0, 5]),
        tilted("Head", "face_bolt_l", [4.18, 26.05, -4.62], [0.44, 0.44, 0.38], "hardware",
               rot=[0, 0, -5]),

        # ---- flip-up visor assembly on the "visor" bone.
        # Hinge pivot [0, 28.80, -4.2], rehung with the raised shell.
        # The frame stops at the cheekbone (y 25.60) rather than running down
        # past the mouth — long enough to cover the face opening, short enough
        # not to hang off the jaw.
        tilted("visor", "v_frame", [-3.95, 25.60, -5.90], [7.90, 3.20, 0.95], "hardware",
               rot=[7, 0, 0]),
        tilted("visor", "v_glass", [-3.35, 25.95, -6.18], [6.70, 2.45, 0.48], "glass_tint",
               rot=[7, 0, 0]),
        tilted("visor", "v_hood", [-4.45, 28.45, -5.95], [8.90, 0.60, 1.95], "hardware",
               rot=[-18, 0, 0]),
        tilted("visor", "v_arm_r", [-4.82, 26.00, -5.20], [0.64, 2.90, 2.15], "hardware",
               rot=[0, 0, -6]),
        tilted("visor", "v_arm_l", [4.18, 26.00, -5.20], [0.64, 2.90, 2.15], "hardware",
               rot=[0, 0, 6]),
    ]
)

# ----------------------------------------------------------------- untar ----
UNTAR = (
    dome("Head", "shell", -4.70, 4.70, -4.70, 4.70, 28.35, 33.40, "un_blue",
         corner=1.16, bevel=1.40, plate=1.40, taper=0.0, flare=1.55)
    + [
        # all-round brim, each edge tipped slightly downward so the rim reads
        # as a curve rather than a shelf
        tilted("Head", "brim_n", [-4.48, 27.95, -5.08], [8.96, 0.78, 1.10], "un_blue_dark",
               rot=[-9, 0, 0]),
        tilted("Head", "brim_s", [-4.48, 27.95, 3.98], [8.96, 0.78, 1.10], "un_blue_dark",
               rot=[9, 0, 0]),
        tilted("Head", "brim_e", [3.98, 27.95, -4.48], [1.10, 0.78, 8.96], "un_blue_dark",
               rot=[0, 0, -9]),
        tilted("Head", "brim_w", [-5.08, 27.95, -4.48], [1.10, 0.78, 8.96], "un_blue_dark",
               rot=[0, 0, 9]),
    ]
    + corner_posts("Head", "brim", -4.98, 4.98, -4.98, 4.98, 27.95, 0.78, 1.42, 1.45,
                   "un_blue_dark")
    + [
        # front panel carries the insignia
        tilted("Head", "front_panel", [-2.55, 29.30, -4.82], [5.10, 2.35, 0.34], "un_blue",
               rot=[-6, 0, 2],
               decal={"face": "north", "type": "roundel", "color": (206, 214, 222)}),

        plain("Head", "bolt_r", [-4.82, 29.55, -1.30], [0.35, 0.55, 0.55], "hardware"),
        plain("Head", "bolt_l", [4.47, 29.55, -1.30], [0.35, 0.55, 0.55], "hardware"),

        # short chin straps down the sides of the jaw to a cup under the chin
        # cover seams crossing the crown on opposite Y rotations — the one
        # place on this helmet where the geometry is not axis-aligned, and it
        # does more for the silhouette than anything bolted to the sides
        tilted("Head", "seam_a", [-0.35, 33.10, -1.85], [0.70, 0.38, 3.70], "un_blue_dark",
               rot=[0, 25, 0]),
        tilted("Head", "seam_b", [-0.35, 33.10, -1.85], [0.70, 0.38, 3.70], "un_blue_dark",
               rot=[0, -25, 0]),

        # cloth cover ties, tipped up off the shell
        tilted("Head", "tie_r", [-4.88, 29.30, -1.05], [0.34, 0.55, 2.20], "un_blue_dark",
               rot=[0, 0, 8]),
        tilted("Head", "tie_l", [4.54, 29.30, -1.05], [0.34, 0.55, 2.20], "un_blue_dark",
               rot=[0, 0, -8]),

        # rear nape adjuster, hanging back off the brim line
        tilted("Head", "nape_strap", [-2.45, 27.30, 3.95], [4.90, 0.75, 0.62], "webbing",
               rot=[-15, 0, 0]),
        tilted("Head", "nape_buckle", [-0.72, 27.50, 4.32], [1.44, 0.58, 0.52], "hardware",
               rot=[-15, 0, 0]),

        # goggle band across the shell, canted with the brim
        tilted("Head", "band_r", [-4.80, 30.10, -2.40], [0.30, 0.85, 5.10], "webbing",
               rot=[0, 0, 6]),
        tilted("Head", "band_l", [4.50, 30.10, -2.40], [0.30, 0.85, 5.10], "webbing",
               rot=[0, 0, -6]),
    ]
    # proper two-point chinstrap replacing the four stub straps
    + chinstrap("Head", "strap", 4.54, 28.05, 24.90, "webbing", "hardware",
                z_front=-2.60, z_back=0.65, width=0.50, splay=5.0,
                front_rake=6.0, back_rake=8.0,
                cup_z=-2.90, cup=(7.60, 0.80, 0.0))
    + [
    ]
)

HELMET_MODELS = {
    "bastion": (BASTION, 128, 91101,
                [("Head", "armorHead", [0, 24, 0]),
                 ("nvg", "Head", [0, 31.75, -4.45])]),
    "k63":     (K63, 128, 91102,
                [("Head", "armorHead", [0, 24, 0]),
                 ("visor", "Head", [0, 28.80, -4.2])]),
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
            # The longer visor needs more travel to clear the eyes: at -50 the
            # bottom of the frame still sits across the line of sight.
            "bones": {"visor": {"rotation": {
                "0.0": {"vector": [0, 0, 0]},
                "0.1": {"vector": [-64, 0, 0]},
                "0.25": {"vector": [-58, 0, 0]},
                "0.4": {"vector": [-64, 0, 0]},
                "0.5": {"vector": [-62, 0, 0]},
            }}},
        },
        "helmet_closed": {
            "loop": "hold_on_last_frame",
            "animation_length": 0.5,
            "bones": {"visor": {"rotation": {
                "0.0": {"vector": [-62, 0, 0]},
                "0.1": {"vector": [-12, 0, 0]},
                "0.25": {"vector": [5, 0, 0]},
                "0.4": {"vector": [-2, 0, 0]},
                "0.5": {"vector": [0, 0, 0]},
            }}},
        },
    },
}
