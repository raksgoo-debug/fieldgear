#!/usr/bin/env python3
"""Preview sheets for the three helmets, including the ZSh visor-open pose."""

import math
import os

import numpy as np

import render_preview as rp

HERE = os.path.dirname(os.path.abspath(__file__))


def rotate_bone(cubes, pivot, deg_x):
    """Bake a bone rotation into cube corners so the open visor can be previewed.
    Cubes stay axis-aligned in-game; this is only for the still image, so we
    rotate the origin and keep the box, which is close enough to read the pose."""
    a = math.radians(deg_x)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for c in cubes:
        o = list(c["origin"])
        s = c["size"]
        # rotate the cube centre about the pivot, keep the box axis-aligned
        cx = o[0] + s[0] / 2
        cy = o[1] + s[1] / 2 - pivot[1]
        cz = o[2] + s[2] / 2 - pivot[2]
        ny = ca * cy - sa * cz
        nz = sa * cy + ca * cz
        d = dict(c)
        d["origin"] = [cx - s[0] / 2, ny + pivot[1] - s[1] / 2, nz + pivot[2] - s[2] / 2]
        if c.get("rotation"):
            # carry the cube's own tilt, and swing its pivot with the bone
            py = c["pivot"][1] - pivot[1]
            pz = c["pivot"][2] - pivot[2]
            d["pivot"] = [c["pivot"][0],
                          ca * py - sa * pz + pivot[1],
                          sa * py + ca * pz + pivot[2]]
            d["rotation"] = [c["rotation"][0] + deg_x, c["rotation"][1], c["rotation"][2]]
        out.append(d)
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)

    for name in ("bastion", "k63", "untar"):
        geo, tex = rp.load(name)
        cubes = rp.collect_cubes(geo)
        rp.sheet([rp.render(cubes, tex, 460, yaw=-26, pitch=8),
                  rp.render(cubes, tex, 460, yaw=-90, pitch=8),
                  rp.render(cubes, tex, 460, yaw=170, pitch=10)],
                 os.path.join(HERE, f"preview/helmet_{name}.png"))

    # ZSh visor down vs visor flipped up (what helmet_open plays)
    geo, tex = rp.load("k63")
    shell = rp.collect_cubes(geo, {"Head"})
    visor = rp.collect_cubes(geo, {"visor"})
    closed = shell + visor
    opened = shell + rotate_bone(visor, [0, 27.9, -4.2], -50)
    rp.sheet([rp.render(closed, tex, 460, yaw=-26, pitch=8),
              rp.render(opened, tex, 460, yaw=-26, pitch=8),
              rp.render(opened, tex, 460, yaw=-88, pitch=8)],
             os.path.join(HERE, "preview/k63_visor_toggle.png"))
