"""Full-system mockup: bottle filter hanging on the tank, pump, feed and return hoses.

Uses the real part geometry from ../build_filter_cap.py, adds stand-in models of the tank,
bottle, filter media, pump and tubing, and writes:
  filter_mockup.glb          coloured 3D scene (open in any glTF viewer / macOS Quick Look)
  filter_mockup_scene.json   key positions, used for the CADCraft layout drawing

    python build_mockup.py     (run from this folder)
Frame: cap axis at the origin, Z up, tank glass at +Y, tank interior beyond it. Units: mm.
"""
import json
import os
import sys

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import build_filter_cap as fc  # noqa: E402

# --- Scene layout -------------------------------------------------------------
G0 = fc.BOTTLE_R + 2.0               # outside face of the glass
G1 = G0 + fc.CLIP_GLASS              # inside face of the glass (mockup uses the clip's glass)
RIM = fc.HOOK_H                      # top of the tank glass
TANK_H = 250.0
FLOOR = RIM - TANK_H
WATER = RIM - 20.0
TANK_X = (-120.0, 120.0)
TANK_D = 200.0                       # tank depth shown (front to back)
BOTTLE_H = 205.0                     # 500 ml soda bottle, lip to base
OVER_RIM = RIM + 28.0                # hoses arc this high over the rim
PUMP = dict(x=-55.0, w=40.0, d=28.0, h=34.0)   # small submersible pump on the floor
CLIP_X = 55.0                        # return clip position along the rim


def tm(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def revolve(profile, segs=96):
    return Manifold.revolve(CrossSection([profile]), segs)


def bottle():
    """PET bottle with a PCO-1881 neck: lip at the cap's gasket seat, body below."""
    lip = fc.H_SKIRT - fc.GASKET_T
    prof = [(0, lip - BOTTLE_H), (fc.BOTTLE_R - 4, lip - BOTTLE_H), (fc.BOTTLE_R, lip - BOTTLE_H + 6),
            (fc.BOTTLE_R, lip - 75), (17, lip - 30), (12.6, lip - 22),
            (16.5, lip - 21), (16.5, lip - 19), (12.6, lip - 18),     # neck support flange
            (12.6, lip), (10.85, lip), (10.85, lip - 22), (15.5, lip - 30),
            (fc.BOTTLE_R - 1.5, lip - 75), (fc.BOTTLE_R - 1.5, lip - BOTTLE_H + 7),
            (fc.BOTTLE_R - 5, lip - BOTTLE_H + 1.5), (0, lip - BOTTLE_H + 1.5)]
    return revolve(prof)


def media():
    """Filter floss / sponge filling the bottle body (the dip tube runs through it)."""
    lip = fc.H_SKIRT - fc.GASKET_T
    m = revolve([(0, lip - BOTTLE_H + 4), (fc.BOTTLE_R - 2, lip - BOTTLE_H + 4),
                 (fc.BOTTLE_R - 2, lip - 80), (0, lip - 80)])
    return m - fc.cyl(fc.DIP_R_OUT + 0.3, -400, 100, -fc.PORT_X)


def pump():
    """Generic mini submersible pump stuck to the glass, outlet nozzle pointing up."""
    x, w, d, h = PUMP["x"], PUMP["w"], PUMP["d"], PUMP["h"]
    y0 = G1 + 8
    body = box(x - w / 2, y0, FLOOR, x + w / 2, y0 + d, FLOOR + h)
    for i in range(5):  # intake slots on the front
        sx = x - w / 2 + 6 + i * 7
        body -= box(sx, y0 + d - 1.5, FLOOR + 4, sx + 3.5, y0 + d + 1, FLOOR + 16)
    nozzle = fc.cyl(3.6, FLOOR + h - 0.01, FLOOR + h + 14, x, y0 + d / 2)
    cups = Manifold()
    for cx in (x - w / 4, x + w / 4):  # suction cups against the glass
        cups += Manifold.cylinder(8, 3, 7, 48).rotate((90, 0, 0)).translate((cx, G1 + 8, FLOOR + h / 2))
    return body + nozzle, cups, (x, y0 + d / 2, FLOOR + h + 14)


def chaikin(pts, n=5):
    p = np.asarray(pts, float)
    for _ in range(n):
        q = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        q.append(p[-1])
        p = np.array(q)
    return p


def hose(points, od=fc.HOSE_OD, segs=20):
    """Tube mesh swept along a smoothed path with parallel-transport frames."""
    path = chaikin(points)
    t = np.gradient(path, axis=0)
    t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.cross(t[0], [1, 0, 0] if abs(t[0][0]) < 0.9 else [0, 1, 0])
    n /= np.linalg.norm(n)
    rings, r = [], od / 2
    ang = np.linspace(0, 2 * np.pi, segs, endpoint=False)
    for i, p in enumerate(path):
        if i:
            n = n - np.dot(n, t[i]) * t[i]
            n /= np.linalg.norm(n)
        b = np.cross(t[i], n)
        rings.append(p + r * (np.cos(ang)[:, None] * n + np.sin(ang)[:, None] * b))
    v = np.vstack(rings)
    f = []
    for i in range(len(path) - 1):
        for j in range(segs):
            a, b2 = i * segs + j, i * segs + (j + 1) % segs
            f += [[a, b2, b2 + segs], [a, b2 + segs, a + segs]]
    v = np.vstack([v, path[0], path[-1]])
    c0, c1 = len(v) - 2, len(v) - 1
    last = (len(path) - 1) * segs
    for j in range(segs):
        f += [[c0, (j + 1) % segs, j], [c1, last + j, last + (j + 1) % segs]]
    return trimesh.Trimesh(v, np.array(f)), path


def build_scene():
    g0, g1, _, yc = fc.clip_frame()
    barb_top = 33.0                                   # hose pushed down over all 3 barb ridges
    parts = {}
    parts["cap"] = tm(fc.build_cap())
    parts["tank_hook"] = tm(fc.build_hook(print_pose=False))
    parts["return_clip"] = tm(fc.build_return_clip(print_pose=False).translate((CLIP_X, 0, 0)))
    parts["dip_tube"] = tm(fc.build_dip_tube().translate((-fc.PORT_X, 0, fc.H_SKIRT - fc.DIP_LEN)))
    parts["bottle"] = tm(bottle())
    parts["media"] = tm(media())
    pump_body, cups, nozzle_top = pump()
    parts["pump"] = tm(pump_body)
    parts["suction_cups"] = tm(cups)
    parts["glass"] = tm(box(TANK_X[0], G0, FLOOR, TANK_X[1], G1, RIM))
    parts["tank_floor"] = tm(box(TANK_X[0], G0, FLOOR - 6, TANK_X[1], G1 + TANK_D, FLOOR))
    parts["water"] = tm(box(TANK_X[0], G1, FLOOR, TANK_X[1], G1 + TANK_D, WATER))

    mid = (G0 + G1) / 2
    px, py, pz = nozzle_top
    feed_pts = [(px, py, pz - 10), (px, py, pz + 20), (px, py, WATER + 10), (px, py, RIM + 10),
                (px * 0.6, mid, OVER_RIM), (-fc.PORT_X - 8, 10, OVER_RIM - 4),
                (-fc.PORT_X, 0, barb_top + 18), (-fc.PORT_X, 0, barb_top), (-fc.PORT_X, 0, 22.0)]
    ret_pts = [(fc.PORT_X, 0, 22.0), (fc.PORT_X, 0, barb_top), (fc.PORT_X, 0, barb_top + 18),
               (fc.PORT_X + 10, 10, OVER_RIM - 4), (CLIP_X * 0.8, mid, OVER_RIM),
               (CLIP_X, yc, RIM + 8), (CLIP_X, yc, RIM - fc.CLIP_IN_L - 4)]   # ends just below the clip
    parts["feed_hose"], feed_path = hose(feed_pts)
    parts["return_hose"], ret_path = hose(ret_pts)

    info = dict(G0=G0, G1=G1, RIM=RIM, FLOOR=FLOOR, WATER=WATER, BOTTLE_H=BOTTLE_H,
                lip=fc.H_SKIRT - fc.GASKET_T, pump=PUMP, pump_y=G1 + 8, nozzle_top=nozzle_top,
                clip_x=CLIP_X, clip_yc=yc, feed_path=feed_path.tolist(), return_path=ret_path.tolist())
    return parts, info


COLORS = {  # RGBA 0-1
    "cap": (0.15, 0.45, 0.85, 1), "tank_hook": (0.95, 0.5, 0.1, 1), "return_clip": (0.95, 0.5, 0.1, 1),
    "dip_tube": (0.2, 0.7, 0.3, 1), "bottle": (0.8, 0.9, 1.0, 0.2), "media": (0.95, 0.7, 0.25, 0.45),
    "pump": (0.2, 0.2, 0.22, 1), "suction_cups": (0.85, 0.85, 0.85, 0.8),
    "glass": (0.7, 0.9, 0.9, 0.12), "tank_floor": (0.25, 0.22, 0.2, 1), "water": (0.3, 0.6, 0.9, 0.1),
    "feed_hose": (0.9, 0.15, 0.15, 1), "return_hose": (0.1, 0.55, 0.95, 1),
}

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    parts, info = build_scene()
    scene = trimesh.Scene()
    for name, mesh in parts.items():
        c = COLORS[name]
        mat = trimesh.visual.material.PBRMaterial(baseColorFactor=[int(v * 255) for v in c],
                                                  alphaMode="BLEND" if c[3] < 1 else "OPAQUE",
                                                  metallicFactor=0.0, roughnessFactor=0.6,
                                                  doubleSided=True)
        mesh.visual = trimesh.visual.TextureVisuals(material=mat)
        # glTF is Y-up: rotate Z-up mm scene into Y-up metres
        mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
        mesh.apply_scale(0.001)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    scene.export("filter_mockup.glb")
    with open("filter_mockup_scene.json", "w") as f:
        json.dump(info, f, indent=1)
    print("wrote filter_mockup.glb, filter_mockup_scene.json;", len(parts), "parts")
