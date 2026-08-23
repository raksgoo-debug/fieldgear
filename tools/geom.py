#!/usr/bin/env python3
"""Geometry helpers for building rounded, faceted shapes out of Bedrock cubes.

Everything here emits cube tuples in the pipeline's format:

    (bone, name, origin, size, material, extras)

where `extras` may carry {"rot": [rx, ry, rz], "pivot": [x, y, z], "decal": {...}}.

Rotation convention is the one the mod's own models use, verified by rendering
killa / beta7_nvg / nato_shturmovik under four candidate conventions and keeping
the only coherent one: Euler XYZ, applied in that order, no sign flips, about
the cube's own pivot.

The reason this file exists: 87% of the cubes in the shipped models carry a
rotation. Axis-aligned boxes alone cannot produce the chamfered silhouette the
mod's helmets have.
"""

import math

R2 = math.sqrt(2.0)


def _c(bone, name, origin, size, mat, rot=None, pivot=None, decal=None):
    extras = {}
    if rot:
        extras["rot"] = [round(v, 4) for v in rot]
        extras["pivot"] = [round(v, 4) for v in (pivot or [0, 0, 0])]
    if decal:
        extras["decal"] = decal
    return (bone, name, [round(v, 4) for v in origin],
            [round(v, 4) for v in size], mat, extras) if extras else \
           (bone, name, [round(v, 4) for v in origin],
            [round(v, 4) for v in size], mat)


def corner_posts(bone, prefix, x0, x1, z0, z1, y, h, c, t, mat):
    """Four vertical plates rotated 45 degrees about Y, bridging the corners of
    an x/z footprint so the cross-section reads as an octagon instead of a box."""
    out = []
    L = c * R2                       # chord length across the cut corner
    specs = [
        ("fr", x1 - c / 2, z0 + c / 2, -45),   # +x / -z
        ("fl", x0 + c / 2, z0 + c / 2, +45),   # -x / -z
        ("br", x1 - c / 2, z1 - c / 2, +45),   # +x / +z
        ("bl", x0 + c / 2, z1 - c / 2, -45),   # -x / +z
    ]
    for tag, mx, mz, ang in specs:
        out.append(_c(bone, f"{prefix}_post_{tag}",
                      [mx - L / 2, y, mz - t / 2], [L, h, t], mat,
                      rot=[0, ang, 0], pivot=[mx, y, mz]))
    return out


def top_chamfers(bone, prefix, x0, x1, z0, z1, ytop, b, t, mat, ends=None,
                 corner_c=None, rise=None):
    """Four sloping slabs, one per top edge, so the crown falls away instead of
    ending in a hard rim.

    Each slab's top face runs from (ytop, edge + b) down to (ytop - rise, edge),
    so its length is hypot(b, rise) and its tilt is atan(rise / b).

    `rise` defaults to `b`, the 45-degree case. Setting it *smaller* than `b`
    is what makes a crown read as a dome rather than a plateau at gameplay
    scale: the silhouette is set by how far the top draws in, not by how tall
    the chamfer is, and a short helmet has no height to spend.
    """
    rise = b if rise is None else rise
    L = math.hypot(b, rise)
    ang = math.degrees(math.atan2(rise, b))
    # Each slab stops short of the corners. Running them full width makes
    # neighbouring slabs cross and poke spikes out of the crown.
    #
    # Inset by the corner cut *plus* the inset the ring makes as it rises. The
    # slab is a rectangle but the octagon it caps narrows with height, so ends
    # inset by only the corner cut sit inside the footprint at the bottom of
    # the chamfer and outside it at the top — poking out as small wings on the
    # crown's corners. Paying the inset up front trades that for a shortfall at
    # the outer rim, which lands against the vertical wall below and hides.
    cc = corner_c if corner_c else b * 0.75
    e = (cc + b) if ends is None else ends
    ax0, ax1 = x0 + e, x1 - e
    az0, az1 = z0 + e, z1 - e
    out = [
        # north edge (-z): pivot on the inboard top edge, front edge swings down
        _c(bone, f"{prefix}_ch_n", [ax0, ytop - t, z0 + b - L], [ax1 - ax0, t, L], mat,
           rot=[-ang, 0, 0], pivot=[(ax0 + ax1) / 2, ytop, z0 + b]),
        # south edge (+z)
        _c(bone, f"{prefix}_ch_s", [ax0, ytop - t, z1 - b], [ax1 - ax0, t, L], mat,
           rot=[ang, 0, 0], pivot=[(ax0 + ax1) / 2, ytop, z1 - b]),
        # east edge (+x)
        _c(bone, f"{prefix}_ch_e", [x1 - b, ytop - t, az0], [L, t, az1 - az0], mat,
           rot=[0, 0, -ang], pivot=[x1 - b, ytop, (az0 + az1) / 2]),
        # west edge (-x)
        _c(bone, f"{prefix}_ch_w", [x0 + b - L, ytop - t, az0], [L, t, az1 - az0], mat,
           rot=[0, 0, ang], pivot=[x0 + b, ytop, (az0 + az1) / 2]),
    ]
    # diagonal facets closing the four corner notches the insets leave behind,
    # continuing the octagon up through the crown
    # Sit them on the SAME corner chord as the octagon ring they cap. Using a
    # smaller cut here puts the facet outboard of the octagon below it, which
    # shows up as a nub sticking out of the crown.
    out += corner_facets(bone, f"{prefix}_cnr", x0, x1, z0, z1, ytop, b, t, mat,
                         cc, rise)
    return out


def euler_xyz_from_basis(bx, by, bz):
    """Euler XYZ angles (degrees) for the rotation whose axes are the given
    orthonormal basis vectors, matching the convention the geo format uses
    (M = Rx . Ry . Rz, applied about the cube's own pivot).

    Fracture Point's own crown corners carry angles like [-79.43, -44.0, -7.53];
    those are what this produces, and what a vertical filler cube cannot.
    """
    m = [[bx[0], by[0], bz[0]],
         [bx[1], by[1], bz[1]],
         [bx[2], by[2], bz[2]]]
    ry = math.asin(max(-1.0, min(1.0, m[0][2])))
    rx = math.atan2(-m[1][2], m[2][2])
    rz = math.atan2(-m[0][1], m[0][0])
    return [math.degrees(rx), math.degrees(ry), math.degrees(rz)]


def corner_facets(bone, prefix, x0, x1, z0, z1, ytop, b, t, mat, c, rise=None):
    """Four sloping facets closing the corners of a chamfer ring.

    The ring below is an octagon: each corner is already a flat cut of chord
    width c, not a point. So the piece that caps it is a flat plate spanning
    from that outer chord (at ytop - b) to the corresponding chord on the inset
    footprint above it (at ytop). Both endpoints are known exactly, which is the
    point — sizing these by eye is what left the corners looking like wedges
    stuck on top of the crown.

    The ring insets by b on *each* horizontal axis while rising by `rise`, so
    across the corner the surface travels b*sqrt(2) horizontally. Its normal is
    therefore proportional to (sx*rise, 2b, sz*rise). At rise == b that reduces
    to (sx, 2, sz)/sqrt(6) — 54.7 degrees up from horizontal for a 35.26-degree
    surface. Using (sx, 1, sz)/sqrt(3) instead, the obvious guess, tilts the
    plate out of the surface so one end finishes above ytop, which is what put
    the row of little spikes along the crown.
    """
    rise = b if rise is None else rise
    out = []
    diag = 1.0 / math.sqrt(2.0)
    # Exactly the corner chord — no wider.
    #
    # Widening it past the chord looks harmless in a large preview and is not:
    # the extra length runs along the chord, so both ends push out beyond the
    # octagon and read as small wings on the crown's top corners. At 30 pixels
    # on a player's head that is the most visible thing about the helmet.
    L = c * R2
    depth = math.sqrt(2 * b * b + rise * rise)   # outer chord to inner chord
    specs = [
        ("fr", 1.0, -1.0),   # +x / -z
        ("fl", -1.0, -1.0),  # -x / -z
        ("br", 1.0, 1.0),    # +x / +z
        ("bl", -1.0, 1.0),   # -x / +z
    ]
    for tag, sx, sz in specs:
        n = (sx * rise, 2.0 * b, sz * rise)    # outward and up
        ln = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        n = (n[0] / ln, n[1] / ln, n[2] / ln)
        u = (-sz * diag, 0.0, sx * diag)       # along the chord
        w = (u[1] * n[2] - u[2] * n[1],        # up-slope
             u[2] * n[0] - u[0] * n[2],
             u[0] * n[1] - u[1] * n[0])
        rot = euler_xyz_from_basis(u, n, w)
        ox = (x1 - c / 2) if sx > 0 else (x0 + c / 2)
        oz = (z1 - c / 2) if sz > 0 else (z0 + c / 2)
        # centre = halfway between the outer chord and the inner one above it,
        # then sunk half a thickness so the outer face lands on the surface
        cx = ox - sx * b / 2 - n[0] * t / 2
        cy = ytop - rise / 2 - n[1] * t / 2
        cz = oz - sz * b / 2 - n[2] * t / 2
        out.append(_c(bone, f"{prefix}_{tag}",
                      [cx - L / 2, cy - t / 2, cz - depth / 2],
                      [L, t, depth], mat,
                      rot=rot, pivot=[cx, cy, cz]))
    return out


def _oct_ring(bone, prefix, x0, x1, z0, z1, y, h, corner, plate, mat):
    """One octagonal slice: two crossed boxes for the flats, four rotated posts
    for the cut corners."""
    return [
        _c(bone, f"{prefix}_x", [x0, y, z0 + corner],
           [x1 - x0, h, (z1 - z0) - 2 * corner], mat),
        _c(bone, f"{prefix}_z", [x0 + corner, y, z0],
           [(x1 - x0) - 2 * corner, h, z1 - z0], mat),
    ] + corner_posts(bone, prefix, x0, x1, z0, z1, y, h, corner, plate, mat)


def dome(bone, prefix, x0, x1, z0, z1, ybot, ytop, mat,
         corner=1.1, bevel=1.2, plate=1.3, taper=0.45, cap_mat=None,
         crown_steps=2, flare=1.0):
    """A rounded, faceted dome.

    Octagonal in plan, tapered inward as it rises, and finished with a
    two-step chamfered crown rather than a flat plateau. Built the way a
    Blockbench modeller would: crossed boxes make the octagon's flats, rotated
    posts cut its corners, and rotated slabs bridge every change of section.

    The taper and the two crown steps are what stop it reading as a stack of
    boxes — a single chamfer still leaves a visible rim.
    """
    cap_mat = cap_mat or mat
    # One step gives a blunt crown that falls straight from the shoulder to the
    # cap; two stack a second, shallower chamfer on top for a taller dome.
    if crown_steps == 1:
        b1, b2 = 0.0, bevel
    else:
        b1 = bevel * 0.62                 # lower crown step
        b2 = bevel - b1                   # upper crown step
    body = (ytop - b1 - b2) - ybot
    lower_h = body * 0.55
    upper_h = body - lower_h - taper
    y_taper = ybot + lower_h              # where the shell starts drawing in
    y_upper = y_taper + taper
    y_crown = y_upper + upper_h           # top of the shell, base of the crown

    slab = plate * 0.72
    if taper <= 0:
        # Straight wall all the way to the crown. This is what a short helmet
        # needs: a vanilla head is 8 wide, so any inset below y 32 pulls the
        # shell inside the head's own corners and the player's skin shows
        # through them. With the crown only a unit or so above the head there is
        # nowhere to put a taper that is not over the head.
        up_corner = corner
        out = _oct_ring(bone, f"{prefix}_lo", x0, x1, z0, z1, ybot,
                        y_crown - ybot, corner, plate, mat)
    else:
        out = _oct_ring(bone, f"{prefix}_lo", x0, x1, z0, z1, ybot, lower_h,
                        corner, plate, mat)
        # taper ring: same chamfer trick, full footprint to the inset one
        up_corner = max(0.6, corner - taper * 0.5)
        out += top_chamfers(bone, f"{prefix}_tp", x0, x1, z0, z1,
                            y_upper, taper, slab, mat, corner_c=corner)
        out += _oct_ring(bone, f"{prefix}_up", x0 + taper, x1 - taper,
                         z0 + taper, z1 - taper, y_upper, upper_h,
                         up_corner, plate, mat)

    # Crown. `flare` is how far each step draws in per unit it rises: at 1.0 the
    # chamfers are 45 degrees, above that they draw in faster than they climb.
    #
    # That knob exists because the silhouette of a dome is set by how small the
    # top gets, not by how tall the chamfer is — and a helmet worn high has
    # almost no height to spend above the skull. At 45 degrees a 1.4-unit crown
    # only pulls in 1.4, which on a 9-wide shell is a plateau with a bevelled
    # edge; it looks domed at 400 pixels and flat at 30, which is the size that
    # matters.
    i1, i2 = b1 * flare, b2 * flare
    t0, t1 = taper, taper + i1
    if b1 > 0:
        out += top_chamfers(bone, f"{prefix}_c1", x0 + t0, x1 - t0, z0 + t0, z1 - t0,
                            y_crown + b1, i1, slab, mat, corner_c=up_corner,
                            rise=b1)
    crown_c = max(0.5, up_corner - i1 * 0.5)
    out += top_chamfers(bone, f"{prefix}_c2", x0 + t1, x1 - t1, z0 + t1, z1 - t1,
                        ytop, i2, slab, mat, corner_c=crown_c, rise=b2)
    # The flat top. Octagonal like every other slice — a plain box here leaves
    # four square corners standing outside the chamfer ring that caps it.
    inset = t1 + i2
    cap_c = max(0.4, crown_c - i2 * 0.5)
    out += _oct_ring(bone, f"{prefix}_cap", x0 + inset, x1 - inset,
                     z0 + inset, z1 - inset, ytop - b2, b2, cap_c, slab, cap_mat)
    return out


def chinstrap(bone, prefix, x_out, y_top, y_bot, mat, buckle_mat,
              z_front=-2.60, z_back=0.60, width=0.50, depth=0.95,
              splay=15.0, front_rake=5.0, back_rake=20.0,
              cup_z=-2.95, cup=(6.80, 0.85, 3.25), buckle=True):
    """Four-point retention: a strap in front of each ear and one behind, both
    leaning inward to a band under the jaw.

    Two things make this read as webbing rather than as four furniture legs.

    First, **every strap pivots at its top edge, not its centre.** A centre
    pivot swings the top outward by as much as it swings the bottom in, so the
    straps tear away from the shell they are supposed to hang off; from the top
    the attachment stays put and only the free end moves.

    Second, the geometry has to actually close. The straps hang at `x_out`,
    just outboard of the 8-wide head so they hug the jaw, and the splay has to
    carry the bottom in far enough to reach the jaw band: `h * sin(splay)` must
    cover the gap to `cup[0] / 2`, or the straps end in mid-air beside the chin.

    Signs: a positive Z rotation swings a cube's bottom toward +x, so the inward
    lean is `-side * splay`; a positive X rotation swings it toward -z, so both
    straps rake forward and the rear one rakes harder to reach the jaw from
    behind the ear.
    """
    h = y_top - y_bot
    cw, ch, cd = cup
    out = []
    for side in (-1.0, 1.0):                      # -1 = the -x side
        x = (x_out - width) if side > 0 else -x_out
        tag = "l" if side > 0 else "r"
        for suffix, z, rake, sp in (("f", z_front, front_rake, splay),
                                    ("b", z_back, back_rake, splay - 2.0)):
            out.append(_c(bone, f"{prefix}_{tag}{suffix}",
                          [x, y_bot, z], [width, h, depth], mat,
                          rot=[rake, 0, -side * sp],
                          pivot=[x + width / 2, y_top, z + depth / 2]))
        # jaw rail: runs fore-and-aft along the jawline, tying the two straps
        # on this side together and carrying on to meet the chin band
        out.append(_c(bone, f"{prefix}_{tag}j",
                      [x + width * 0.10, y_bot - ch * 0.55, cup_z - 1.30],
                      [width * 0.90, ch * 1.05, (z_back - cup_z) + 2.20], mat,
                      rot=[0, 0, -side * 5.0],
                      pivot=[x + width / 2, y_bot, 0.0]))
    # chin band, crossing the FRONT of the face. It cannot go under the jaw:
    # the head is a solid 8-cube down to y 24, so anything tucked beneath it is
    # simply inside the head and never drawn.
    out.append(_c(bone, f"{prefix}_band", [-cw / 2, y_bot - ch * 1.05, cup_z - 1.35],
                  [cw, ch, 0.55], mat, rot=[-7, 0, 0],
                  pivot=[0, y_bot, cup_z - 1.05]))
    if buckle:
        out.append(_c(bone, f"{prefix}_buckle",
                      [-0.80, y_bot - ch * 1.22, cup_z - 1.72],
                      [1.60, 0.92, 0.62], buckle_mat, rot=[-7, 0, 0],
                      pivot=[0, y_bot, cup_z - 1.05]))
    return out


def tilted(bone, name, origin, size, mat, rot, pivot=None, decal=None):
    """A single cube with a small deliberate tilt — brow lips, visor rakes,
    rail angles. The mod leans on 2.5 / 5 / 7.5 degree tilts for exactly this."""
    if pivot is None:
        pivot = [origin[0] + size[0] / 2, origin[1] + size[1] / 2, origin[2] + size[2] / 2]
    return _c(bone, name, origin, size, mat, rot=rot, pivot=pivot, decal=decal)


def plain(bone, name, origin, size, mat, decal=None):
    return _c(bone, name, origin, size, mat, decal=decal)
