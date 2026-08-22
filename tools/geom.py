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


def _oct_ring(bone, prefix, x0, x1, z0, z1, y, h, corner, plate, mat):
    """One octagonal slice: two crossed boxes for the flats, four rotated posts
    for the cut corners. Only ever rotated about Y."""
    return [
        _c(bone, f"{prefix}_x", [x0, y, z0 + corner],
           [x1 - x0, h, (z1 - z0) - 2 * corner], mat),
        _c(bone, f"{prefix}_z", [x0 + corner, y, z0],
           [(x1 - x0) - 2 * corner, h, z1 - z0], mat),
    ] + corner_posts(bone, prefix, x0, x1, z0, z1, y, h, corner, plate, mat)


def dome(bone, prefix, x0, x1, z0, z1, ybot, ytop, mat,
         rings=6, corner=1.15, curve=0.82, cap_mat=None):
    """A rounded dome built as a stack of octagonal rings on a spherical profile.

    Earlier versions bridged each change of section with 45-degree slabs
    rotated about X and Z. That produced a clean profile face-on but left a
    notch at all four corners, where a sloping slab met a vertical corner
    facet — visible in game as a step out of the crown.

    This builds the curve out of many small steps instead. Every cube is
    either axis-aligned or rotated about Y only, so nothing can cross at a
    corner and there is nothing to notch. At 16 px per block a step of about a
    third of a unit reads as a smooth surface.
    """
    cap_mat = cap_mat or mat
    cx = (x0 + x1) / 2.0
    cz = (z0 + z1) / 2.0
    half_x = (x1 - x0) / 2.0
    half_z = (z1 - z0) / 2.0
    height = ytop - ybot
    out = []

    for i in range(rings):
        # sample the profile at the middle of each ring so the steps straddle
        # the ideal surface rather than sitting entirely inside it
        u = (i + 0.5) / rings
        factor = math.sqrt(max(0.04, 1.0 - (u * curve) ** 2))
        hx = half_x * factor
        hz = half_z * factor
        ry = ybot + height * (i / rings)
        rh = height / rings
        # overlap each ring slightly into the one above so no seam can open up
        if i < rings - 1:
            rh *= 1.06
        c = max(0.5, corner * factor)
        out += _oct_ring(bone, f"{prefix}_r{i}", cx - hx, cx + hx, cz - hz, cz + hz,
                         ry, rh, c, c * 0.85, mat)

    # a small flat crown closes the top
    top_u = 1.0
    tf = math.sqrt(max(0.04, 1.0 - (top_u * curve) ** 2)) * 0.72
    out.append(_c(bone, f"{prefix}_cap",
                  [cx - half_x * tf, ytop - height / rings * 0.45, cz - half_z * tf],
                  [2 * half_x * tf, height / rings * 0.5, 2 * half_z * tf], cap_mat))
    return out


def tilted(bone, name, origin, size, mat, rot, pivot=None, decal=None):
    """A single cube with a small deliberate tilt — brow lips, visor rakes,
    rail angles. The mod leans on 2.5 / 5 / 7.5 degree tilts for exactly this."""
    if pivot is None:
        pivot = [origin[0] + size[0] / 2, origin[1] + size[1] / 2, origin[2] + size[2] / 2]
    return _c(bone, name, origin, size, mat, rot=rot, pivot=pivot, decal=decal)


def plain(bone, name, origin, size, mat, decal=None):
    return _c(bone, name, origin, size, mat, decal=decal)
