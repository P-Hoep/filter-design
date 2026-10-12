# 04: Verification

## What has been verified (in software only)
| Check | Result | How |
|---|---|---|
| All 5 STLs watertight | yes | `save()` output (`trimesh.is_watertight`) |
| Thread is right-handed with a 2.7 pitch | yes | Sliced the thread void at z = 1.0/1.3/1.6/1.9. The crest angle moves **+40° CCW per 0.3 mm**, which is right-hand and 360°/2.7 mm |
| Cap ∩ hook volume | 0 | manifold intersection (`(cap ^ hook).volume()`) |
| Intake hose clearances | hose ∩ bottle 0, hose ∩ gasket 0; hose edge r ≤ 10.46 in the neck (bore r 10.85) | manifold intersection on the mockup hose mesh, plus the path radius |
| Hook ∩ glass | 52 mm³, expected | Just the 2 mm inner-corner chamfer against a square glass edge |
| Refactors left geometry unchanged | yes | Hook volume 17.76 cm³ and clip 4.78 cm³ were identical before and after the refactors |
| Return hose path folds | fixed | Asserted the end of the path's z is monotonic |
| Video streams | h264 1280×720 + AAC + mov_text, 79.5 s | ffprobe |
| Captions in sync with shots | yes | Contact sheet of frames at 5/25/45/68 s |

Reference figures (current parameters): cap ~274k tris, 11.63 cm³ (with intake barb); hook 17.76 cm³;
clip 4.78 cm³; gasket 0.49 cm³.

## NOT verified (no physical test yet)
- Thread fit on a real bottle. The dimensions are from published spec, not measured.
- Gasket seal under pump pressure; PETG porosity at 100% infill.
- Barb grip on real tubing, especially pushing 1/4" tubing onto the Ø7.2 intake barb inside the skirt.
- Clip grip force on real glass; hook creep under constant load.
- Real flow rate through 4.4 mm bores plus media with a real pump.
- Printability of the intake barb (a free-standing column from the bed to the ceiling) and the ~28 mm ceiling bridge.

## Re-check snippets
Run these from `filter-design/` with the geometry venv.

Thread handedness (expect the angle to *increase* with z):
```python
import numpy as np, math, build_filter_cap as b
m = b.thread_void(0, 5.4)
for z in (1.0, 1.3, 1.6, 1.9):
    p = np.vstack([np.asarray(q) for q in m.slice(z).to_polygons()])
    r = np.hypot(p[:,0], p[:,1]); inner = p[r < b.R_CREST + 0.02]
    th = np.arctan2(inner[:,1], inner[:,0])
    print(z, round(math.degrees(math.atan2(np.sin(th).mean(), np.cos(th).mean())), 1))
```

Interference (expect 0):
```python
import build_filter_cap as b
cap = b.build_cap(); hook = b.build_hook(print_pose=False)
print((cap ^ hook).volume())
```

Also check the clip in place: `b.build_return_clip(print_pose=False)` against a glass slab
`Manifold.cube((80, b.CLIP_GLASS, 40)).translate((-40, b.BOTTLE_R + 2, b.HOOK_H - 40))`. Expect
about 46 mm³: the 0.6 mm grip ridge (intentional interference) plus the 1.5 mm inner-corner chamfer
against the square glass edge.

Visual check: render the mockup GLB with Blender (`render_flythrough.py -- preview`), or use
matplotlib `Poly3DCollection` for a quick look. The cap mesh is heavy (~272k tris) but works.

## Suggested physical test order (to tell the user)
1. Print only the bottom ~8 mm of the cap (or a thread-test ring) and check the fit on a bottle.
2. Print the full cap and gasket. Plug the barbs, pressurize by squeezing, check for leaks.
3. Fit the intake hose. Run the full filter over a sink for 24 h.
4. Hang it with the hook and clip on the tank.
