#!/usr/bin/env python3
"""Renders each helmet on a plain head with the eye line marked.

Vanilla heads span y 24..32 and the eyes sit at about y 28. A shell whose rim
falls below that line covers the face, which is the failure being checked for.
"""
import math, os, sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image
import render_preview as rp

UV = {f: {"uv": [0, 0], "uv_size": [1, 1]} for f in
      ("north", "south", "east", "west", "up", "down")}

def box(o, s):
    return {"origin": o, "size": s, "uv": UV}

def flat(rgb):
    t = np.zeros((2, 2, 3)); t[:, :] = rgb; return t

HEAD = [box([-4, 24, -4], [8, 8, 8])]
EYELINE = [box([-4.02, 27.9, -4.05], [8.04, 0.22, 8.1])]

def render_groups(groups, size=430, yaw=-22, pitch=4):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    def view(p):
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        x2 = cy*x + sy*z; z2 = -sy*x + cy*z
        return np.stack([x2, cp*y - sp*z2, sp*y + cp*z2], axis=-1)
    L = np.array([-0.4, 0.8, -0.55]); L /= np.linalg.norm(L)
    pts = []
    for cubes, _ in groups:
        for c in cubes:
            o = np.array(c["origin"], float); s = np.array(c["size"], float)
            M = rp.cube_matrix(c["rotation"]) if c.get("rotation") else None
            piv = np.array(c.get("pivot", [0, 0, 0]), float)
            for dx in (0, 1):
                for dy in (0, 1):
                    for dz in (0, 1):
                        p = o + s*np.array([dx, dy, dz])
                        if M is not None: p = M @ (p - piv) + piv
                        pts.append(p)
    pts = view(np.array(pts))
    minx, maxx = pts[:, 0].min(), pts[:, 0].max()
    miny, maxy = pts[:, 1].min(), pts[:, 1].max()
    span = max(maxx-minx, maxy-miny)*1.1
    scale = size/span; ox = (minx+maxx)/2; oy = (miny+maxy)/2
    color = np.zeros((size, size, 3)); depth = np.full((size, size), 1e9)
    for cubes, tex in groups:
        for c in cubes:
            o = np.array(c["origin"], float); s = np.array(c["size"], float)
            M = rp.cube_matrix(c["rotation"]) if c.get("rotation") else None
            piv = np.array(c.get("pivot", [0, 0, 0]), float)
            for face, (normal, corner, ue, ve) in rp.FACE_INFO.items():
                fu = c["uv"][face]; ux, uy = fu["uv"]; uw, uh = fu["uv_size"]
                wu = float(np.linalg.norm(s*np.abs(np.array(ue, float))))
                wv = float(np.linalg.norm(s*np.abs(np.array(ve, float))))
                n = max(2, int(wu*scale*2.2)+2); m = max(2, int(wv*scale*2.2)+2)
                ss, tt = np.meshgrid((np.arange(n)+0.5)/n, (np.arange(m)+0.5)/m)
                base = o + s*np.array(corner, float)
                U = s*np.abs(np.array(ue, float))*np.array(ue, float)
                V = s*np.abs(np.array(ve, float))*np.array(ve, float)
                P = base[None,None,:] + ss[...,None]*U[None,None,:] + tt[...,None]*V[None,None,:]
                nrm = np.array(normal, float)
                if M is not None:
                    P = np.einsum("ij,abj->abi", M, P - piv) + piv
                    nrm = M @ nrm
                Pr = view(P)
                sx = ((Pr[...,0]-ox)*scale + size/2).astype(int)
                sy_ = (size/2 - (Pr[...,1]-oy)*scale).astype(int)
                dz = Pr[...,2]
                nv = view(np.array([nrm]))[0]
                lam = 0.45 + 0.55*max(0.0, float(np.dot(nv/np.linalg.norm(nv), L)))
                tx = np.clip((ux + ss*uw).astype(int), 0, tex.shape[1]-1)
                ty = np.clip((uy + tt*uh).astype(int), 0, tex.shape[0]-1)
                texel = tex[ty, tx]*lam
                okm = (sx>=0)&(sx<size)&(sy_>=0)&(sy_<size)
                fx, fy, fd, fc = sx[okm], sy_[okm], dz[okm], texel[okm]
                order = np.argsort(-fd)
                fx, fy, fd, fc = fx[order], fy[order], fd[order], fc[order]
                keep = fd < depth[fy, fx]
                depth[fy[keep], fx[keep]] = fd[keep]; color[fy[keep], fx[keep]] = fc[keep]
    bg = np.array([26,27,30], float)
    return Image.fromarray(np.where(depth[...,None]<1e8, color, bg).clip(0,255).astype(np.uint8))

if __name__ == "__main__":
    panels = []
    for name in ("bastion", "k63", "untar"):
        geo, tex = rp.load(name)
        groups = [(HEAD, flat((196, 160, 130))), (EYELINE, flat((200, 60, 60))),
                  (rp.collect_cubes(geo), tex)]
        panels.append(render_groups(groups, 430, yaw=-22))
        panels.append(render_groups(groups, 430, yaw=-90))
    rp.sheet(panels, "preview/fit_check.png")
