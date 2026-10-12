# 03: Toolchain, Workflow and Gotchas

## Environment (as found on 2026-10-11, macOS / Apple Silicon)
| Tool | Where | Used for |
|---|---|---|
| CADCraft MCP (`mcp__cadcraft__*`) | MCP server, headless | 2D engineering drawings (DXF/PNG) |
| Python 3.8 venv with `manifold3d numpy trimesh matplotlib` | was created in a session scratchpad (gone now) | Geometry → STL, GLB, previews |
| Python 3.12 venv with `kokoro-onnx soundfile` | session scratchpad (gone now) | Narration |
| Blender | `/Applications/Blender.app/Contents/MacOS/Blender` (supports `-b` headless) | Stills and flythrough frames |
| ffmpeg / ffprobe | `/opt/homebrew/bin` (**no `drawtext`/`subtitles` filters**: no freetype/libass) | Video assembly |
| espeak-ng | `/opt/homebrew` | Needed by Kokoro's phonemizer |
| Kokoro model | `~/leroy-ant/pixa-video/models/kokoro-v1.0.onnx` + `voices-v1.0.bin` | TTS |

The venvs were in a temporary scratchpad. Recreate them:
```
python3 -m venv .venv && .venv/bin/pip install manifold3d numpy trimesh matplotlib pillow
/opt/homebrew/bin/python3.12 -m venv .venv-tts && .venv-tts/bin/pip install kokoro-onnx soundfile
```
(The default pyenv python is 3.8. kokoro-onnx needs 3.10 or newer, hence Homebrew 3.12.)

## Regenerating everything
Run from `filter-design/`:
```
.venv/bin/python build_filter_cap.py               # all 5 STLs (cap takes ~30 s: dense thread)
cd mockup && ../.venv/bin/python build_mockup.py    # filter_mockup.glb + filter_mockup_scene.json
cd video
../../.venv-tts/bin/python narrate.py               # narration.wav + timing.json
Blender -b --python render_flythrough.py -- preview # sanity check: 1 frame per shot -> frames/preview_*.png
Blender -b --python render_flythrough.py            # ~1850 frames, ~0.6 s each = ~18 min
../../.venv/bin/python make_video.py                # filter_flythrough.mp4 + .srt (in mockup/video/)
```
`make_video.py` writes the MP4 to `mockup/video/`. The user keeps a copy at the repo root, so
copy it there after regenerating. `frames/` and `captions/` are intermediates; delete them after.

## How the geometry code works (`build_filter_cap.py`)
- **manifold3d** for robust booleans. `cyl()`, `dovetail()`, `extrude_yz()` (extrudes a (Y,Z)
  profile along X via an explicit axis-permutation `transform`), `lay_flat()` (print pose).
- **Thread**: `thread_void()` builds one cross-section whose radius follows the tooth profile
  around 360° (`r(θ) = R_BORE − tooth(−θ·P/2π)`), then `Manifold.extrude(..., twist_degrees=+360·turns)`.
  **The sign matters:** `twist_degrees` positive = right-hand thread with this section. The
  first attempt used a negative twist and produced a left-hand thread; it was caught by slicing (see 04).
- Cap order of operations: body + barbs → subtract grip grooves → add rail → subtract thread,
  gasket pocket, chamfer, socket, bores. Adding the rail *after* the grooves keeps it solid.
  Subtracting the bore *after* the rail keeps the web out of the interior.
- `save()` converts to trimesh and prints the triangle count, `watertight`, volume and bounds. Read that line.

## Mockup (`mockup/build_mockup.py`)
- Imports `build_filter_cap` through `sys.path` (parent dir), so the scene always uses the current
  part geometry.
- Hoses: a polyline smoothed by Chaikin subdivision, then swept as a tube with parallel-transport
  frames (`hose()`). **Keep waypoint z monotonic at the hose ends.** An earlier return path went
  down to the clip bottom and then *up* to the water line, folding the tube back on itself.
- GLB export: per-part `PBRMaterial` (alphaMode BLEND for glass/water/bottle/media), rotated
  Z-up → glTF Y-up and scaled mm → m. Blender's glTF importer restores Z-up, so **Blender
  world coords = mockup mm / 1000.**
- Also writes `filter_mockup_scene.json` (glass/rim/floor positions, pump position, hose paths)
  for the 2D layout drawing.

## Video pipeline (`mockup/video/`)
- `shots.json`: 8 shots `{text, cam:[start,end], look:[start,end]}` in mockup mm.
- `narrate.py`: Kokoro `af_heart`, 0.3 s lead + 0.7 s tail per line. Writes `timing.json`.
  **Gotcha:** kokoro-onnx's bundled espeak looks for data at a CI build path
  (`/Users/runner/work/espeakng-loader/...`) and dies. The script sets
  `ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data` to fix that.
- `render_flythrough.py`: Eevee (`BLENDER_EEVEE_NEXT`, falls back to `BLENDER_EEVEE`), 24 fps,
  1280×720, 24 samples, **view transform "Standard"**, background (0.42,0.47,0.55). Filmic/AgX
  plus a light background made the transparent scene look washed out. Camera uses Track-To on an
  empty, with two keyframes per shot (Bezier easing within the shot, hard cut between shots).
  Materials set to blended transparency (`surface_render_method`, or `blend_method` on older Blender).
- `make_video.py`: the frame count per shot is `round(dur·24)`, identical to the renderer, so
  captions line up. Captions are drawn as full-frame RGBA PNGs with Pillow and overlaid with
  `overlay=enable='between(t,a,b)'`, because this ffmpeg lacks drawtext/subtitles. Also muxes
  the `.srt` as `mov_text`. Fade in/out. libx264 crf 20, AAC 160k.

## CADCraft usage notes
- Use a **metric** drawing (`new_drawing {metric:true}`).
- Fastest input is the `script` tool with AutoCAD syntax, one command per line, blank line =
  Enter: `pline x,y x,y ... c`, `rectang`, `circle`, `line ... ` + blank line.
- **These failed in script mode:** `-layer m NAME c 7 NAME` (option keywords rejected, though
  layers still got created) and `pline w 9.5 9.5 ...` (width option rejected). Use
  `execute` instead: `layer.new`, `layer.set`, `layer.current`, and `pedit {handles, option:"width", width}`.
- `layer.set linetype:"HIDDEN"` fails until the linetype is loaded (`linetype {load:"HIDDEN"}`).
- `mleader` text ignores `properties.set height`. It came out unreadably small, so it was replaced
  with `line` + `mtext` (where `height` works). Use `\\P` for line breaks in mtext.
- Dimensions: set `dimstyle {name:"Standard", DIMTXT, DIMASZ, ...}` first. `%%c` gives Ø, `%%d` gives °.
- A small hatch scale renders as a solid fill. Use `hatchedit {scale: ...}` bigger (0.5 worked
  for the small section, 8 for the large media block).
- `qselect {type, layer}` returns handles, which you can then pass to `properties.set {handles, layer}`.
- The PNG preview renderer **drops spaces in text**. That's a preview artefact; the DXF text is intact.
- Entities created by `script` land on the **current** layer. Set it before drawing.
- Save: `save {path: "...dxf"}` and `save {path: "...png"}` (PNG export keeps the drawing name).

## The two CADCraft drawings
1. `bottle_filter_cap.dxf`: Section A-A through the ports (layers BODY/HIDDEN/DIMS/NOTES):
   wall/plate/barb profiles with ANSI31 hatch, thread teeth (left/right offset half a pitch), gasket,
   ghost bottle neck and dip tube. Top view at (55,10) with the rail. Hook side view at x≈100 to 160.
2. `mockup/installation_layout.dxf`: side elevation (Y horizontal, Z vertical) generated from
   `filter_mockup_scene.json`. Layers TANK/BOTTLE/MEDIA/DIP/PRINTED/PUMP/FEED/RETURN/NOTES.
   Hoses are 9.5-wide polylines (the curves show jaggies in the preview from short segments).
