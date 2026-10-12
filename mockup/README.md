# Bottle Canister Filter: System Mockup

How the filter, pump and hoses go together on the tank. The printed parts are the real
geometry from `../build_filter_cap.py`. The tank, bottle, pump and tubing are stand-ins.

| File | What it is |
|------|------------|
| `installation_layout.dxf` / `.png` | CADCraft side elevation with every part labelled: where the pump sits, how each hose is routed, hook and clip positions |
| `filter_mockup.glb` | Coloured 3D scene. Open with macOS Quick Look/Preview, Blender, or any glTF viewer |
| `mockup_overview.png`, `mockup_side.png`, `mockup_closeup.png` | Still renders |
| `../filter_flythrough.mp4` | Narrated flythrough (Kokoro voice `af_heart`) with captions and a subtitle track. `video/make_video.py` writes it to `video/`; copy it to the repo root |
| `video/filter_flythrough.blend` | The animated Blender scene the flythrough is rendered from (written by `render_flythrough.py`) |
| `filter_mockup_stills.blend` | Blender scene for the still renders, plus a `parts_preview` scene for `../bottle_filter_assembly_preview.png` |
| `build_mockup.py` | Rebuilds the scene. Layout values are at the top (tank size, pump and clip positions) |

## Routing
1. **Pump**: on the tank floor, stuck to the glass right behind the filter, outlet pointing up.
2. **Feed hose (red)**: from the pump straight up the inside of the glass, over the rim, and down onto the cap's **inlet** barb (the one with the intake barb underneath).
3. **Inside the bottle**: the intake hose (red, the same tubing pushed onto the barb under the inlet) releases the water at the bottom, and it rises up through the media.
4. **Return hose (blue)**: from the cap's **outlet** barb, up over the rim, down through the **return clip**, ending just under the water surface. Ending it near the surface ripples the water, which adds oxygen.
5. **Hook**: slides up onto the cap's rail and hangs over the rim next to the hoses. The clip goes a few cm along the rim from the hook.

Keep the hose arcs over the rim short and smooth. Kinks and long runs cost a lot of flow with a small pump.

## Rebuild
```
python build_mockup.py                                    # scene + filter_mockup.glb
cd video
python narrate.py                                         # Kokoro narration (kokoro-onnx, soundfile)
Blender -b --python render_flythrough.py                  # frames/ (add "-- preview" for one frame per shot)
python make_video.py                                      # filter_flythrough.mp4 + .srt
```
`narrate.py` looks for `kokoro-v1.0.onnx` and `voices-v1.0.bin` in `$KOKORO_DIR`
(default `~/leroy-ant/pixa-video/models`). Narration lines and camera paths are in `video/shots.json`.
