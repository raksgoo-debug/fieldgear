#!/usr/bin/env python3
"""Software preview renderer: rasterises the generated .geo.json + texture
so the geometry and UV mapping can be eyeballed without launching Minecraft."""

import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, "out/assets/fracturepoint/geo/item/armor")
TEX = os.path.join(HERE, "out/assets/fracturepoint/textures/item/armor")

FACE_INFO = {
    # normal, origin corner offset (in fractions of size), U edge, V edge
    "north": ((0, 0, -1), (1, 1, 0), (-1, 0, 0), (0, -1, 0)),
    "south": ((0, 0, 1), (0, 1, 1), (1, 0, 0), (0, -1, 0)),
    "west":  ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, -1, 0)),
    "east":  ((1, 0, 0), (1, 1, 1), (0, 0, -1), (0, -1, 0)),
    "up":    ((0, 1, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1)),
    "down":  ((0, -1, 0), (0, 0, 1), (1, 0, 0), (0, 0, -1)),
}


def load(model):
    with open(os.path.join(GEO, f"{model}.geo.json")) as fh:
        geo = json.load(fh)["minecraft:geometry"][0]
    tex = np.asarray(Image.open(os.path.join(TEX, f"{model}.png")).convert("RGB")).astype(float)
    return geo, tex


def collect_cubes(geo, bones_filter=None):
    out = []
    for b in geo["bones"]:
        if bones_filter and b["name"] not in bones_filter:
            continue
        for c in b.get("cubes", []):
            out.append(c)
    return out


def _axis(a, k):
    c, s_ = math.cos(a), math.sin(a)
    if k == "x":
        return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])
    if k == "y":
        return np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])


def cube_matrix(rot):
    """Euler XYZ about the cube's own pivot — verified against the mod's own
    models (see rotconv.py); the other three candidate conventions render
    killa / beta7_nvg as exploded geometry."""
    M = np.eye(3)
    for i, k in enumerate("xyz"):
        M = M @ _axis(math.radians(rot[i]), k)
    return M


def render(cubes, tex, size=520, yaw=-32.0, pitch=14.0, light=(-0.4, 0.8, -0.55)):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def rot(p):
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        x2 = cy * x + sy * z
        z2 = -sy * x + cy * z
        y3 = cp * y - sp * z2
        z3 = sp * y + cp * z2
        return np.stack([x2, y3, z3], axis=-1)

    L = np.array(light, dtype=float)
    L /= np.linalg.norm(L)

    # world bounds -> fit
    pts = []
    for c in cubes:
        o = np.array(c["origin"], float)
        s = np.array(c["size"], float)
        M = cube_matrix(c["rotation"]) if c.get("rotation") else None
        piv = np.array(c.get("pivot", [0, 0, 0]), float)
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    p = o + s * np.array([dx, dy, dz])
                    if M is not None:
                        p = M @ (p - piv) + piv
                    pts.append(p)
    pts = rot(np.array(pts))
    minx, maxx = pts[:, 0].min(), pts[:, 0].max()
    miny, maxy = pts[:, 1].min(), pts[:, 1].max()
    span = max(maxx - minx, maxy - miny) * 1.12
    scale = size / span
    ox = (minx + maxx) / 2
    oy = (miny + maxy) / 2

    color = np.zeros((size, size, 3), float)
    depth = np.full((size, size), 1e9)

    for c in cubes:
        o = np.array(c["origin"], float)
        s = np.array(c["size"], float)
        M = cube_matrix(c["rotation"]) if c.get("rotation") else None
        piv = np.array(c.get("pivot", [0, 0, 0]), float)
        for face, (normal, corner, ue, ve) in FACE_INFO.items():
            fu = c["uv"][face]
            ux, uy = fu["uv"]
            uw, uh = fu["uv_size"]
            # sample densely enough to cover every screen pixel the face lands on
            wu = float(np.linalg.norm(s * np.abs(np.array(ue, float))))
            wv = float(np.linalg.norm(s * np.abs(np.array(ve, float))))
            n = max(2, int(wu * scale * 2.2) + 2)
            m = max(2, int(wv * scale * 2.2) + 2)
            ss, tt = np.meshgrid((np.arange(n) + 0.5) / n, (np.arange(m) + 0.5) / m)

            base = o + s * np.array(corner, float)
            U = s * np.abs(np.array(ue, float)) * np.array(ue, float)
            V = s * np.abs(np.array(ve, float)) * np.array(ve, float)
            P = (base[None, None, :]
                 + ss[..., None] * U[None, None, :]
                 + tt[..., None] * V[None, None, :])
            nrm = np.array(normal, float)
            if M is not None:
                P = np.einsum("ij,abj->abi", M, P - piv) + piv
                nrm = M @ nrm
            Pr = rot(P)

            sx = ((Pr[..., 0] - ox) * scale + size / 2).astype(int)
            sy_ = (size / 2 - (Pr[..., 1] - oy) * scale).astype(int)
            dz = Pr[..., 2]

            nr = rot(np.array([nrm], float))[0]
            lam = 0.42 + 0.58 * max(0.0, float(np.dot(nr / np.linalg.norm(nr), L)))

            tx = np.clip((ux + ss * uw).astype(int), 0, tex.shape[1] - 1)
            ty = np.clip((uy + tt * uh).astype(int), 0, tex.shape[0] - 1)
            texel = tex[ty, tx] * lam

            ok = (sx >= 0) & (sx < size) & (sy_ >= 0) & (sy_ < size)
            fx, fy, fd, fc = sx[ok], sy_[ok], dz[ok], texel[ok]
            order = np.argsort(-fd)
            fx, fy, fd, fc = fx[order], fy[order], fd[order], fc[order]
            keep = fd < depth[fy, fx]
            depth[fy[keep], fx[keep]] = fd[keep]
            color[fy[keep], fx[keep]] = fc[keep]

    bg = np.array([26, 27, 30], float)
    img = np.where(depth[..., None] < 1e8, color, bg)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


def sheet(panels, path, pad=12):
    w = sum(p.width for p in panels) + pad * (len(panels) + 1)
    h = max(p.height for p in panels) + pad * 2
    out = Image.new("RGB", (w, h), (18, 19, 21))
    x = pad
    for p in panels:
        out.paste(p, (x, pad))
        x += p.width + pad
    out.save(path)
    print("wrote", path, out.size)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)

    scav, t_scav = load("scav")
    uni, t_uni = load("scav_uniform")
    pads, t_pads = load("scav_shoulderpads")

    helmet = collect_cubes(scav, {"Head"})
    chest = collect_cubes(scav, {"Body"})

    sheet([render(helmet, t_scav, 420, yaw=-28),
           render(helmet, t_scav, 420, yaw=150),
           render(helmet, t_scav, 420, yaw=-90)],
          os.path.join(HERE, "preview/helmet.png"))

    sheet([render(chest, t_scav, 420, yaw=-28),
           render(chest, t_scav, 420, yaw=155),
           render(chest, t_scav, 420, yaw=-90)],
          os.path.join(HERE, "preview/chestplate.png"))

    sheet([render(collect_cubes(uni), t_uni, 420, yaw=-28),
           render(collect_cubes(uni), t_uni, 420, yaw=155)],
          os.path.join(HERE, "preview/uniform.png"))

    sheet([render(collect_cubes(pads), t_pads, 420, yaw=-28),
           render(collect_cubes(pads), t_pads, 420, yaw=155)],
          os.path.join(HERE, "preview/shoulderpads.png"))
