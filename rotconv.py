#!/usr/bin/env python3
"""Work out which Euler convention the mod's .geo.json cube rotations use, by
rendering one of the mod's own models under each candidate and eyeballing which
produces a coherent helmet instead of an exploded mess."""

import json
import math
import os
import sys

import numpy as np
from PIL import Image

SRC = "/tmp/fp/assets/fracturepoint"
FACE_INFO = {
    "north": ((0, 0, -1), (1, 1, 0), (-1, 0, 0), (0, -1, 0)),
    "south": ((0, 0, 1), (0, 1, 1), (1, 0, 0), (0, -1, 0)),
    "west":  ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, -1, 0)),
    "east":  ((1, 0, 0), (1, 1, 1), (0, 0, -1), (0, -1, 0)),
    "up":    ((0, 1, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1)),
    "down":  ((0, -1, 0), (0, 0, 1), (1, 0, 0), (0, 0, -1)),
}


def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def cube_matrix(rot, conv):
    """conv: (order, sx, sy, sz) — axis order applied left-to-right, plus sign
    flips per axis."""
    order, sx, sy, sz = conv
    a = {"x": rx(math.radians(rot[0] * sx)),
         "y": ry(math.radians(rot[1] * sy)),
         "z": rz(math.radians(rot[2] * sz))}
    M = np.eye(3)
    for ax in order:
        M = M @ a[ax]
    return M


def collect(model):
    geo = json.load(open(f"{SRC}/geo/item/armor/{model}.geo.json"))["minecraft:geometry"][0]
    cubes = []
    for b in geo["bones"]:
        for c in b.get("cubes", []):
            cubes.append(c)
    tex = np.asarray(Image.open(f"{SRC}/textures/item/armor/{model}.png")
                     .convert("RGB")).astype(float)
    return cubes, tex, geo["description"]


def render(cubes, tex, conv, size=420, yaw=-30, pitch=10, bones_y=None):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p):
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        x2 = cy * x + sy * z
        z2 = -sy * x + cy * z
        y3 = cp * y - sp * z2
        z3 = sp * y + cp * z2
        return np.stack([x2, y3, z3], axis=-1)

    L = np.array([-0.4, 0.8, -0.55])
    L /= np.linalg.norm(L)

    prepared = []
    pts = []
    for c in cubes:
        o = np.array(c["origin"], float)
        s = np.array(c["size"], float)
        rot = c.get("rotation")
        piv = np.array(c.get("pivot", [0, 0, 0]), float)
        M = cube_matrix(rot, conv) if rot else None
        prepared.append((c, o, s, M, piv))
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    p = o + s * np.array([dx, dy, dz])
                    if M is not None:
                        p = M @ (p - piv) + piv
                    pts.append(p)
    pts = view(np.array(pts))
    minx, maxx = pts[:, 0].min(), pts[:, 0].max()
    miny, maxy = pts[:, 1].min(), pts[:, 1].max()
    span = max(maxx - minx, maxy - miny) * 1.08
    scale = size / span
    ox, oy = (minx + maxx) / 2, (miny + maxy) / 2

    color = np.zeros((size, size, 3))
    depth = np.full((size, size), 1e9)
    for c, o, s, M, piv in prepared:
        uvs = c.get("uv")
        if not isinstance(uvs, dict):
            continue
        for face, (normal, corner, ue, ve) in FACE_INFO.items():
            fu = uvs.get(face)
            if not isinstance(fu, dict):
                continue
            ux, uy = fu["uv"]
            uw, uh = fu["uv_size"]
            wu = float(np.linalg.norm(s * np.abs(np.array(ue, float))))
            wv = float(np.linalg.norm(s * np.abs(np.array(ve, float))))
            n = max(2, int(wu * scale * 2.4) + 2)
            m = max(2, int(wv * scale * 2.4) + 2)
            ss, tt = np.meshgrid((np.arange(n) + 0.5) / n, (np.arange(m) + 0.5) / m)
            base = o + s * np.array(corner, float)
            U = s * np.abs(np.array(ue, float)) * np.array(ue, float)
            V = s * np.abs(np.array(ve, float)) * np.array(ve, float)
            P = (base[None, None, :] + ss[..., None] * U[None, None, :]
                 + tt[..., None] * V[None, None, :])
            nr = np.array(normal, float)
            if M is not None:
                P = np.einsum("ij,abj->abi", M, P - piv) + piv
                nr = M @ nr
            Pr = view(P)
            sx_ = ((Pr[..., 0] - ox) * scale + size / 2).astype(int)
            sy_ = (size / 2 - (Pr[..., 1] - oy) * scale).astype(int)
            dz = Pr[..., 2]
            nrv = view(np.array([nr]))[0]
            lam = 0.40 + 0.60 * max(0.0, float(np.dot(nrv / np.linalg.norm(nrv), L)))
            tx = np.clip((ux + ss * uw).astype(int), 0, tex.shape[1] - 1)
            ty = np.clip((uy + tt * uh).astype(int), 0, tex.shape[0] - 1)
            texel = tex[ty, tx] * lam
            okm = (sx_ >= 0) & (sx_ < size) & (sy_ >= 0) & (sy_ < size)
            fx, fy, fd, fc = sx_[okm], sy_[okm], dz[okm], texel[okm]
            order_ = np.argsort(-fd)
            fx, fy, fd, fc = fx[order_], fy[order_], fd[order_], fc[order_]
            keep = fd < depth[fy, fx]
            depth[fy[keep], fx[keep]] = fd[keep]
            color[fy[keep], fx[keep]] = fc[keep]
    bg = np.array([26, 27, 30], float)
    return Image.fromarray(np.where(depth[..., None] < 1e8, color, bg)
                           .clip(0, 255).astype(np.uint8))


CONVENTIONS = {
    "XYZ ++ +": ("xyz", 1, 1, 1),
    "ZYX ++ +": ("zyx", 1, 1, 1),
    "XYZ -- +": ("xyz", -1, -1, 1),
    "ZYX -- +": ("zyx", -1, -1, 1),
}

if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "killa"
    cubes, tex, desc = collect(model)
    # helmet-only: cubes above y=22 keeps the render readable
    head = [c for c in cubes if c["origin"][1] + c["size"][1] > 23]
    panels = []
    for label, conv in CONVENTIONS.items():
        panels.append((label, render(head, tex, conv)))
    pad = 10
    w = sum(p.width for _, p in panels) + pad * (len(panels) + 1)
    out = Image.new("RGB", (w, panels[0][1].height + pad * 2), (18, 19, 21))
    x = pad
    for _, p in panels:
        out.paste(p, (x, pad))
        x += p.width + pad
    out.save(f"preview/conv_{model}.png")
    print("wrote", f"preview/conv_{model}.png", "| order:", list(CONVENTIONS))
