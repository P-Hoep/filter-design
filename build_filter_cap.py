"""Mini canister filter head: screw-on cap for a 28 mm PCO-1881 soda/water bottle.

Builds the 3D solid from the dimensions in bottle_filter_cap.dxf (CADCraft drawing)
and writes printable STLs. Units: mm. Z=0 is the open end of the cap.

    python build_filter_cap.py        (needs: pip install manifold3d numpy trimesh)
"""
import math
import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(96)

# --- Dimensions -------------------------------------------------------------
R_OUT = 17.0          # cap outer radius (34 mm OD)
H_SKIRT = 13.5        # open end to inner ceiling (gasket seat)
H_TOP = 19.5          # overall cap height (6 mm top plate)
R_BORE = 13.95        # thread root radius in cap (27.9 mm)
R_CREST = 12.95       # thread crest radius in cap (25.9 mm); bottle root is ~25.1 mm
PITCH = 2.7           # PCO-1881, single start, right hand
TOOTH_ROOT_W = 1.5    # cap tooth width at root (axial)
TOOTH_CREST_W = 0.5   # cap tooth width at crest
THREAD_TOP = 11.5     # threads stop below the gasket pocket
GASKET_T = 2.0        # gasket pocket depth above thread
PORT_X = 6.5          # inlet at -X, outlet at +X
R_HOLE = 2.2          # 4.4 mm flow bore
R_SOCKET = 3.25       # 6.5 mm socket for 1/4" OD dip tube
SOCKET_TOP = 17.5     # socket depth = 4 mm into top plate
KNURLS, R_KNURL = 30, 0.9
GASKET_ID_R = 10.5    # 21 mm gasket ID clears the dip tube

# Dip tube: carries pump water to the bottom of the bottle so it must rise through all the media
DIP_LEN = 180.0       # below the cap ceiling; set to (bottle height - ~20 mm)
DIP_R_OUT = 3.5       # 7 mm OD fits inside the ~21.7 mm neck bore next to the outlet
DIP_R_IN = 2.2
DIP_SPIGOT_R = 3.15   # 6.3 mm push-fit into the 6.5 mm socket (wrap with PTFE tape)
DIP_SPIGOT_L = 3.8
DIP_NOTCH_W, DIP_NOTCH_H = 2.5, 4.0   # flow notches at the bottom end

# Tank hook: slides up onto a dovetail rail on the cap (+Y side) and hangs over the tank rim
RAIL_Y0, RAIL_Y1 = 20.0, 24.0   # rail from narrow neck (y0) to wide face (y1)
RAIL_W0, RAIL_W1 = 8.0, 16.0    # dovetail widths at y0 / y1 (45 deg flanks print cleanly)
WEB_W = 8.0                     # web joining rail to the cap wall
CLR = 0.25                      # sliding clearance per side
BOTTLE_R = 33.0       # bottle body radius; the hook keeps the bottle this far off the glass
GLASS_T = 12.0        # max tank glass/rim thickness the hook fits over
HOOK_H = 55.0         # tank rim height above the cap's open end
HOOK_W = 26.0         # hook width (X)
HOOK_T = 5.0          # hook plate thickness
LIP_L = 18.0          # how far the lip reaches down inside the tank

# Return-hose clip: clamps on the tank rim and holds the return hose pointing down into the tank
CLIP_GLASS = 6.0      # your actual glass/rim thickness (the clip grips it)
CLIP_GRIP = 0.6       # interference of the grip ridge on the outer leg
CLIP_W = 18.0         # clip width (X)
CLIP_T = 3.0          # leg thickness (thin enough to flex)
CLIP_OUT_L = 15.0     # outer leg length
CLIP_IN_L = 34.0      # inner leg length
HOSE_OD = 9.5         # 1/4" ID vinyl tubing is 3/8" (9.5 mm) OD
HOSE_SNAP = 0.78      # C-ring opening as a fraction of the hose OD


def cyl(r, z0, z1, x=0.0, y=0.0):
    return Manifold.cylinder(z1 - z0, r, r).translate((x, y, z0))


def tooth(u):
    """Radial height (0..depth) of the cap tooth at axial position u in one pitch."""
    depth = R_BORE - R_CREST
    flank = (TOOTH_ROOT_W - TOOTH_CREST_W) / 2
    u %= PITCH
    if u < flank:
        return depth * u / flank
    if u < flank + TOOTH_CREST_W:
        return depth
    if u < TOOTH_ROOT_W:
        return depth * (TOOTH_ROOT_W - u) / flank
    return 0.0


def thread_void(z0, z1):
    """Internal right-hand thread space, made by twist-extruding one helical slice."""
    n = 360
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = R_BORE - tooth(-th / (2 * math.pi) * PITCH)
        pts.append((r * math.cos(th), r * math.sin(th)))
    h = z1 - z0
    turns = h / PITCH
    return Manifold.extrude(CrossSection([pts]), h, n_divisions=int(turns * 90),
                            twist_degrees=360 * turns).translate((0, 0, z0))


def barb(x):
    """Hose barb for 1/4 in ID tubing, revolved from the drawing profile (r, z)."""
    prof = [(0, H_TOP - 0.1), (4.5, H_TOP - 0.1), (4.5, 21.5), (3.0, 21.5), (3.0, 22.5),
            (3.8, 22.5), (3.0, 26.0), (3.8, 26.0), (3.0, 29.5), (3.8, 29.5), (3.0, 33.0),
            (3.0, 35.2), (2.7, 35.5), (0, 35.5)]
    return Manifold.revolve(CrossSection([prof]), 96).translate((x, 0, 0))


def dovetail(y0, y1, w0, w1, z0, z1):
    """Dovetail prism along Z: width w0 at y0 widening to w1 at y1."""
    xs = CrossSection([[(-w0 / 2, y0), (w0 / 2, y0), (w1 / 2, y1), (-w1 / 2, y1)]])
    return Manifold.extrude(xs, z1 - z0).translate((0, 0, z0))


def build_cap():
    body = cyl(R_OUT, 0, H_TOP) + barb(-PORT_X) + barb(PORT_X)
    # grip grooves around the outside
    for k in range(KNURLS):
        a = 2 * math.pi * k / KNURLS
        body -= cyl(R_KNURL, -1, H_TOP - 1.5, (R_OUT + 0.3) * math.cos(a), (R_OUT + 0.3) * math.sin(a))
    # hook rail: web from the cap wall out to a dovetail
    body += Manifold.cube((WEB_W, RAIL_Y0 - 12.0 + 0.01, H_TOP)).translate((-WEB_W / 2, 12.0, 0))
    body += dovetail(RAIL_Y0, RAIL_Y1, RAIL_W0, RAIL_W1, 0, H_TOP)
    # threaded skirt, gasket pocket and a lead-in chamfer
    body -= thread_void(-1.0, THREAD_TOP)
    body -= cyl(R_BORE, THREAD_TOP - 0.01, H_SKIRT)
    body -= Manifold.cylinder(0.8, R_BORE + 0.6, R_BORE, 96).translate((0, 0, -0.01))
    # flow paths
    body -= cyl(R_SOCKET, H_SKIRT - 0.1, SOCKET_TOP, -PORT_X)   # dip-tube socket (inlet)
    body -= cyl(R_HOLE, H_SKIRT - 0.1, 36, -PORT_X)
    body -= cyl(R_HOLE, H_SKIRT - 0.1, 36, PORT_X)
    return body


def build_gasket():
    return cyl(13.75, 0, GASKET_T) - cyl(GASKET_ID_R, -1, GASKET_T + 1)


def build_dip_tube():
    """Printed standing on its notched end; the spigot end pushes into the inlet socket."""
    tube = cyl(DIP_R_OUT, 0, DIP_LEN) + cyl(DIP_SPIGOT_R, DIP_LEN - 0.01, DIP_LEN + DIP_SPIGOT_L)
    tube -= cyl(DIP_R_IN, -1, DIP_LEN + DIP_SPIGOT_L + 1)
    for a in (0, 90):  # 4 notches so the end can't seal against the bottle floor
        tube -= Manifold.cube((DIP_NOTCH_W, 2 * DIP_R_OUT + 2, 2 * DIP_NOTCH_H), center=True).rotate((0, 0, a))
    return tube


def hook_profile():
    """Hook side profile in the (Y, Z) plane of the cap, glass face at y = BOTTLE_R + 2."""
    g0 = BOTTLE_R + 2.0          # outside face of the tank glass
    g1 = g0 + GLASS_T            # inside face of the tank glass
    p0 = g0 - HOOK_T             # back of the hook plate
    s0 = RAIL_Y0 - CLR           # face of the standoff block that holds the dovetail slot
    top = HOOK_H + HOOK_T
    return [(s0, 0), (g0, 0), (g0, HOOK_H - 2), (g0 + 2, HOOK_H), (g1, HOOK_H),
            (g1, HOOK_H - LIP_L), (g1 + HOOK_T, HOOK_H - LIP_L + 1), (g1 + HOOK_T, top),
            (p0, top), (p0, H_TOP + 5), (s0, H_TOP + 5)]


def extrude_yz(pts, width):
    """Extrude a (Y, Z) side profile symmetrically along X."""
    m = Manifold.extrude(CrossSection([pts]), width).translate((0, 0, -width / 2))  # axes (y, z, x)
    return m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])                  # -> (x, y, z)


def lay_flat(m):
    """Print pose: on its side (X up) so layers run the length of the profile, no supports."""
    m = m.rotate((0, 90, 0))
    b = m.bounding_box()
    return m.translate((-b[0], -b[1], -b[2]))


def build_hook(print_pose=True):
    hook = extrude_yz(hook_profile(), HOOK_W)
    hook -= dovetail(RAIL_Y0 - CLR, RAIL_Y1 + CLR, RAIL_W0 + 2 * CLR, RAIL_W1 + 2 * CLR, -1, H_TOP + CLR)
    hook -= Manifold.cube((RAIL_W0 + 2 * CLR, 1.01, H_TOP + CLR + 1)).translate(
        (-(RAIL_W0 / 2 + CLR), RAIL_Y0 - CLR - 1.0, -1))                    # slot mouth
    return lay_flat(hook) if print_pose else hook


def clip_frame():
    """Glass faces and hose ring centre for the return clip, in the same frame as the hook."""
    g0 = BOTTLE_R + 2.0
    g1 = g0 + CLIP_GLASS
    hole_r = HOSE_OD / 2 + 0.2
    yc = g1 + CLIP_T + 1.0 + hole_r
    return g0, g1, hole_r, yc


def clip_profile():
    """Return-clip side profile in the (Y, Z) plane, same frame as the hook."""
    g0, g1, _, _ = clip_frame()
    top = HOOK_H + CLIP_T
    return [(g0 - CLIP_T, HOOK_H - CLIP_OUT_L), (g0 + CLIP_GRIP, HOOK_H - CLIP_OUT_L + 1.5),
            (g0 + CLIP_GRIP, HOOK_H - CLIP_OUT_L + 3), (g0, HOOK_H - CLIP_OUT_L + 4.5),  # grip ridge
            (g0, HOOK_H - 1.5), (g0 + 1.5, HOOK_H), (g1, HOOK_H),
            (g1, HOOK_H - CLIP_IN_L), (g1 + CLIP_T, HOOK_H - CLIP_IN_L), (g1 + CLIP_T, top),
            (g0 - CLIP_T, top)]


def build_return_clip(print_pose=True):
    g0, g1, hole_r, yc = clip_frame()
    clip = extrude_yz(clip_profile(), CLIP_W)
    # snap-in C-ring holding the hose vertically against the inner leg
    z0, z1 = HOOK_H - CLIP_IN_L, HOOK_H - CLIP_IN_L + 16
    ring = Manifold.cube((CLIP_W, yc + hole_r * 0.55 - g1 - CLIP_T + 0.01, z1 - z0)).translate(
        (-CLIP_W / 2, g1 + CLIP_T - 0.01, z0))
    ring -= cyl(hole_r, z0 - 1, z1 + 1, 0, yc)
    ring -= Manifold.cube((HOSE_OD * HOSE_SNAP, 20, z1 - z0 + 2)).translate((-HOSE_OD * HOSE_SNAP / 2, yc, z0 - 1))
    clip += ring
    return lay_flat(clip) if print_pose else clip


def save(m, path):
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    tm.export(path)
    print(f"{path}: {len(tm.faces)} tris, watertight={tm.is_watertight}, "
          f"volume={tm.volume / 1000:.2f} cm3, bounds={np.round(tm.bounds, 2).tolist()}")
    return tm


if __name__ == "__main__":
    save(build_cap(), "bottle_filter_cap.stl")
    save(build_gasket(), "bottle_filter_gasket_tpu.stl")
    save(build_dip_tube(), "bottle_filter_dip_tube.stl")
    save(build_hook(), "bottle_filter_tank_hook.stl")
    save(build_return_clip(), "bottle_filter_return_clip.stl")
