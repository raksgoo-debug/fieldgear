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
                 corner_c=None):
    """Four slabs rotated 45 degrees off horizontal, one per top edge, so the
    crown falls away instead of ending in a hard rim.

    Each slab's top face runs from (ytop, edge + b) down to (ytop - b, edge),
    which is why its length is b*sqrt(2): rotating that length by 45 degrees
    lands it exactly on both endpoints.
    """
    L = b * R2
    # Each slab stops short of the corners. Running them full width makes
    # neighbouring slabs cross and poke spikes out of the crown, because at the
    # corner one slab's top edge sits a full bevel above the other's plane.
    e = b if ends is None else ends
    ax0, ax1 = x0 + e, x1 - e
    az0, az1 = z0 + e, z1 - e
    out = [
        # north edge (-z): pivot on the inboard top edge, front edge swings down
        _c(bone, f"{prefix}_ch_n", [ax0, ytop - t, z0 + b - L], [ax1 - ax0, t, L], mat,
           rot=[-45, 0, 0], pivot=[(ax0 + ax1) / 2, ytop, z0 + b]),
        # south edge (+z)
        _c(bone, f"{prefix}_ch_s", [ax0, ytop - t, z1 - b], [ax1 - ax0, t, L], mat,
           rot=[45, 0, 0], pivot=[(ax0 + ax1) / 2, ytop, z1 - b]),
        # east edge (+x)
        _c(bone, f"{prefix}_ch_e", [x1 - b, ytop - t, az0], [L, t, az1 - az0], mat,
           rot=[0, 0, -45], pivot=[x1 - b, ytop, (az0 + az1) / 2]),
        # west edge (-x)
        _c(bone, f"{prefix}_ch_w", [x0 + b - L, ytop - t, az0], [L, t, az1 - az0], mat,
           rot=[0, 0, 45], pivot=[x0 + b, ytop, (az0 + az1) / 2]),
    ]
    # diagonal facets closing the four corner notches the insets leave behind,
    # continuing the octagon up through the crown
    # Sit them on the SAME corner chord as the octagon ring they cap. Using a
    # smaller cut here puts the facet outboard of the octagon below it, which
    # shows up as a nub sticking out of the crown.
    cc = b if corner_c is None else corner_c
    # Tucked inward and kept short: the facet is vertical while the slabs
    # beside it slope, so sitting flush would leave a visible tab at each
    # corner of the crown.
    k = b * 0.4
    out += corner_posts(bone, f"{prefix}_cnr", x0 + k, x1 - k, z0 + k, z1 - k,
                        ytop - b, b * 0.92, cc, min(t, cc * 0.8), mat)
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
         corner=1.1, bevel=1.2, plate=1.3, taper=0.45, cap_mat=None):
    """A rounded, faceted dome.

    Octagonal in plan, tapered inward as it rises, and finished with a
    two-step chamfered crown rather than a flat plateau. Built the way a
    Blockbench modeller would: crossed boxes make the octagon's flats, rotated
    posts cut its corners, and rotated slabs bridge every change of section.

    The taper and the two crown steps are what stop it reading as a stack of
    boxes — a single chamfer still leaves a visible rim.
    """
    cap_mat = cap_mat or mat
    b1 = bevel * 0.62                     # lower crown step
    b2 = bevel - b1                       # upper crown step
    body = (ytop - b1 - b2) - ybot
    lower_h = body * 0.55
    upper_h = body - lower_h - taper
    y_taper = ybot + lower_h              # where the shell starts drawing in
    y_upper = y_taper + taper
    y_crown = y_upper + upper_h           # top of the shell, base of the crown

    out = _oct_ring(bone, f"{prefix}_lo", x0, x1, z0, z1, ybot, lower_h,
                    corner, plate, mat)
    # taper ring: same chamfer trick, bridging full footprint to the inset one
    up_corner = max(0.6, corner - taper * 0.5)
    slab = plate * 0.72
    out += top_chamfers(bone, f"{prefix}_tp", x0, x1, z0, z1,
                        y_upper, taper, slab, mat, corner_c=corner)
    out += _oct_ring(bone, f"{prefix}_up", x0 + taper, x1 - taper,
                     z0 + taper, z1 - taper, y_upper, upper_h,
                     up_corner, plate, mat)

    # two-step crown
    t0, t1 = taper, taper + b1
    out += top_chamfers(bone, f"{prefix}_c1", x0 + t0, x1 - t0, z0 + t0, z1 - t0,
                        y_crown + b1, b1, slab, mat, corner_c=up_corner)
    out += top_chamfers(bone, f"{prefix}_c2", x0 + t1, x1 - t1, z0 + t1, z1 - t1,
                        ytop, b2, slab, mat, corner_c=max(0.5, up_corner - b1 * 0.5))
    inset = t1 + b2
    out.append(_c(bone, f"{prefix}_cap",
                  [x0 + inset, ytop - b2, z0 + inset],
                  [(x1 - x0) - 2 * inset, b2, (z1 - z0) - 2 * inset], cap_mat))
    return out


def tilted(bone, name, origin, size, mat, rot, pivot=None, decal=None):
    """A single cube with a small deliberate tilt — brow lips, visor rakes,
    rail angles. The mod leans on 2.5 / 5 / 7.5 degree tilts for exactly this."""
    if pivot is None:
        pivot = [origin[0] + size[0] / 2, origin[1] + size[1] / 2, origin[2] + size[2] / 2]
    return _c(bone, name, origin, size, mat, rot=rot, pivot=pivot, decal=decal)


def plain(bone, name, origin, size, mat, decal=None):
    return _c(bone, name, origin, size, mat, decal=decal)
