# Design Notes: Bottle Canister Filter (start here)

Notes for future Claude instances (and humans) picking up this project. Read this file first,
then whichever topic file you need.

## What the project is
A 3D-printable **mini canister filter for small aquariums** built around an ordinary 28 mm
soda/water bottle:

- A printed **filter head (cap)** screws onto the bottle (PCO-1881 thread) and has an inlet and
  an outlet hose barb.
- A small **submersible pump** in the tank pushes water through the **feed hose** to the inlet.
- A printed **dip tube** carries that water to the **bottom of the bottle**, so it has to rise
  through *all* the filter media (this was an explicit user requirement: no bypass).
- Filtered water leaves through the outlet barb and the **return hose** back into the tank.
- The system is sealed (gasket), so it runs pressurized like a real canister filter.
- A printed **tank hook** hangs the whole filter on the outside of the tank rim, and a printed
  **return clip** holds the return hose on the rim.

## Index
| File | Read it when you need... |
|------|--------------------------|
| [01-requirements-and-history.md](01-requirements-and-history.md) | What the user asked for, in order, and how each request was resolved |
| [02-part-specifications.md](02-part-specifications.md) | Every part's dimensions, the reasoning behind them, and print orientation |
| [03-toolchain-and-workflow.md](03-toolchain-and-workflow.md) | How the files are generated (CADCraft, manifold3d, Blender, Kokoro, ffmpeg) and the gotchas hit along the way |
| [04-verification.md](04-verification.md) | What has been checked, how, and the scripts to re-check |
| [05-open-issues-and-ideas.md](05-open-issues-and-ideas.md) | Known risks, untested assumptions, and likely next requests |

## Repository map (`filter-design/`)
```
build_filter_cap.py            SINGLE SOURCE OF TRUTH for all printed geometry -> STLs
bottle_filter_cap.stl          filter head (PETG)
bottle_filter_dip_tube.stl     dip tube (PETG)
bottle_filter_tank_hook.stl    hook, already in print pose (PETG)
bottle_filter_return_clip.stl  rim clip for return hose, already in print pose (PETG)
bottle_filter_gasket_tpu.stl   optional printed gasket (TPU)
bottle_filter_cap.dxf / _drawing.png   CADCraft engineering drawing (section, top view, hook side view)
bottle_filter_assembly_preview.png     matplotlib render of cap + hook + dip tube (made before the clip existed)
filter_flythrough.mp4          narrated video, 720p 7.3 MB (the user copied it here from mockup/video/)
media/filter_flythrough_480p.mp4     compressed video (854x480, crf 30, 1.4 MB) linked from README
media/filter_flythrough_preview.gif  16 s / 2.9 MB teaser (3 clips) shown inline in README
README.md                      public project page: overview, images, GIF -> video link, params
PARTS_LIST.md                  non-printed bill of materials + leak/siphon warning
mockup/                        full-system scene: tank, bottle, pump, hoses (see mockup/README.md)
  build_mockup.py              imports ../build_filter_cap.py; writes filter_mockup.glb + scene json
  installation_layout.dxf/.png CADCraft side-elevation install diagram
  video/                       narration + Blender flythrough + ffmpeg assembly scripts
design-notes/                  this folder
```

## Golden rules for changing the design
1. **Edit parameters in `build_filter_cap.py`**, never the STLs. Re-run it from `filter-design/`.
   Every part derives from the constants at the top, and `mockup/build_mockup.py` imports them too.
2. After a geometry change, re-run the checks in [04-verification.md](04-verification.md):
   watertight STLs, right-hand thread, no part interference.
3. The CADCraft DXFs are **hand-drawn documentation**, not generated from the script. Update them
   if you change dimensions they show (see 03 for how).
4. Don't commit or push unless the user asks. The repo is `github.com/P-Hoep/filter-design`, branch `main`.
5. Units are millimetres everywhere. Cap frame: origin on the cap axis, Z=0 at the cap's open end,
   Z up, tank glass toward +Y, inlet at -X, outlet at +X.
