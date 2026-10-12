# 01: Requirements and Design History

The user's requests, in order, and how each one was resolved. Dates: all of this happened on 2026-10-11.

## R1: Original request
> "using cadcraft mcp, design an aquarium filter that can be a screw top onto a normal pop/water
> bottle. It will function as a mini canister filter... a pump inside the aquarium tube will pump
> water into the bottle, and there will be a return so the whole system is pressurized...
> Create it in cadcraft and save it as an stl for 3d printing"

**Resolution**
- **CADCraft can't produce STLs.** It's a 2D drafting app (AutoCAD clone) with no solids,
  revolve, boolean or STL export (`list_commands` shows only 2D entities plus `3dpoly`/`helix` as
  polylines). So the design is **drawn in CADCraft** (dimensioned section + top view, saved
  as DXF/PNG), and the **3D solid is built in Python with `manifold3d`** from the same numbers.
  The user was told this. Keep doing it this way unless CADCraft gains 3D.
- Cap fits **PCO-1881** (the current standard 28 mm soda neck). Two 1/4" ID hose barbs, a sealing
  gasket seat, and grip ribs.

## R2: Intake must reach the bottle bottom; cap must hang on the tank
> "the intake tube needs to send the water to the bottom of the bottle to make sure it gets
> through all the filter medium, otherwise it will take the path of least resistance... Also,
> the cap should have a way to hang it on the tank"

**Resolution**
- v1 already had a 6.5 mm socket under the inlet for a user-supplied 1/4" OD tube. Added a
  **printed dip tube** (7 mm OD, 4.4 mm bore, `DIP_LEN` = 180 mm) with a push-fit spigot and 4
  bottom notches so it can't seal against the bottle floor.
- Gasket ID widened from 20 to **21 mm** so the dip tube passes beside it.
- Hanging: a hook moulded onto the cap would need supports, and its layers would be loaded in
  peel. Chose a **45° dovetail rail on the cap** plus a **separate hook** printed flat (layers run
  the whole J profile, so it's strong and needs no supports). The hook slides *up* onto the rail;
  the rail's top end bears on the closed top of the slot, so the bottle's weight seats it.

## R3: Full-system mockup + return-hose clip
> "create a subfolder with a complete mockup of where the pump and hoses should go. I think we
> also may want another clip for the return hose to make sure it stays affixed on the tank"

**Resolution**
- `mockup/` holds a 3D scene (`filter_mockup.glb`) built from the real part geometry, with
  stand-ins for the tank, bottle, media, pump and hoses. Also stills and a CADCraft installation
  layout (side elevation, all parts labelled).
- New **return clip**: a rim clamp with a grip ridge and a snap-in C-ring for 9.5 mm OD hose.
  Unlike the hook, it grips the glass, so its gap (`CLIP_GLASS`) must match the user's actual glass.

## R4: Non-printed parts list (mid-turn)
> "also add a non printed parts list to the main folder"

**Resolution:** `PARTS_LIST.md`: bottle, pump spec, tubing, media, gasket, PTFE tape,
optional clamps, rigid tube and flow valve, filament amounts, a printed-parts table, and a
**leak/siphon warning**.

## R5: Narrated flythrough (mid-turn)
> "also create a video flythrough of the model with narration using kokoro"

**Resolution:** a 77 s, 1280×720 MP4. Kokoro (`kokoro-onnx`, voice `af_heart`) narrates 8 lines.
Blender (Eevee, headless) renders one camera move per line, timed to the audio. Pillow draws the
captions and ffmpeg overlays them, plus a soft `mov_text` subtitle track and an `.srt`.

## R6: These notes
> "add complete design notes for future claude instances to a markdown folder in the
> filter-design subfolder"

Before this request, the user moved the whole project into `filter/filter-design/` (now a git repo
with remote `P-Hoep/filter-design`) and copied the MP4 to the repo root.

## R7: Replace the printed dip tube with a barb + flexible tubing
> "There is a fixed tube that goes inside the bottle on the intake which sends it to the bottom.
> Instead lets put another barbed fitting and just use another section of flexible tubing for that
> part. Update the models and the videos and everything."

**Resolution**
- Socket and printed dip tube removed (`bottle_filter_dip_tube.stl` deleted). The cap now has a
  downward **intake barb** under the inlet, and the user pushes a length of the same 1/4" ID
  tubing onto it.
- 1/4" ID tubing is ~10.8 mm OD when stretched over a barb, which doesn't fit beside the old
  ±6.5 inlet inside the ~21.7 mm neck. So the ports became asymmetric: inlet x −4.8, outlet x +7.0.
  The intake barb ridges are Ø7.2 (vs Ø7.6 on top) to keep the hose inside the gasket ID.
- The barb tip is flush with the cap's open end, so it prints standing on the bed (no supports).
- Updated: STLs, mockup GLB (red intake hose), stills, assembly preview (now rendered in Blender),
  both CADCraft drawings (the top view's ports had been drawn at ±11.5; fixed), narration line 4,
  the full flythrough, the 480p video and the GIF, plus the docs. Blender scenes are now saved in the
  repo (`mockup/video/filter_flythrough.blend`, `mockup/filter_mockup_stills.blend`).

## User preferences observed
- Wants **printable, practical** results: STLs ready to slice, BOM, install diagram.
- Thinks in terms of real-world function (flow path, bypass, hanging, hoses popping off).
  Proactively flag functional risks (e.g. siphoning).
- Adds requests mid-task; fold them in without losing the current thread.
- Uses the "craft" MCP apps (CADCraft) and likes visual outputs (drawings, renders, video).
- Prefers off-the-shelf flexible tubing to printed rigid tubes where it works (R7).
- Wants Blender work saved into the project as .blend files, not just rendered headless.
