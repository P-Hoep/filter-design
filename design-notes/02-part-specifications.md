# 02: Part Specifications

All values are constants in `build_filter_cap.py` (names in `CODE`). Units: mm.
Frame: cap axis = Z, Z=0 at the cap's open end, glass toward +Y, inlet at -X, outlet at +X.

## Bottle interface (PCO-1881 assumptions)
These come from published PCO-1881 neck dimensions as I know them, **not measured on a real
bottle.** Test-fit before trusting them (see 05).

| Feature | Value used | Notes |
|---|---|---|
| Neck thread OD | ~27.4 | Cap thread bore is 27.9, about 0.25 radial clearance |
| Neck thread root | ~25.1 | Cap tooth crest 25.9, about 0.4 radial clearance |
| Pitch / starts / hand | 2.7 / 1 / right | |
| Neck bore | ~21.7 | Limits intake-hose placement and media size |
| Lip inner radius | ~10.85 | Gasket ID 21 (r 10.5) must stay inside this |
| Neck support flange OD | ~33 | Skirt kept short (13.5) so it doesn't hit the tamper/flange area |
| Bottle body radius | `BOTTLE_R` 33 | 500 mL soda bottle is about 65 mm; sets hook standoff |

## Filter head / cap: `bottle_filter_cap.stl`
| Feature | Value | Reasoning |
|---|---|---|
| OD / height | 34 (`R_OUT` 17) / 19.5 (`H_TOP`) | 3 mm skirt wall over the thread |
| Skirt depth to ceiling | `H_SKIRT` 13.5 | Thread zone 0 to 11.5 (`THREAD_TOP`), then 2 mm gasket pocket |
| Top plate | 6 | Carries both top barbs and the intake barb |
| Thread | bore r 13.95 (`R_BORE`), crest r 12.95 (`R_CREST`), tooth 1.5 root / 0.5 crest | Thin tooth leaves room for the bottle tooth; 0.3 to 0.4 slop for FDM |
| Lead-in chamfer | 0.6 × 0.8 at the open end | Easier starting |
| Ports | inlet x = −4.8 (`PORT_IN_X`), outlet x = +7.0 (`PORT_OUT_X`), bore 4.4 (`R_HOLE`) | Asymmetric on purpose: the intake hose under the inlet has to fit inside the gasket ID and neck bore (see below). Collars are 2.8 apart, the hoses on the top barbs about 1.2 apart |
| Intake barb | Points **down** from the ceiling under the inlet. 3 ridges Ø7.2 (`IBARB_RIDGE_R`), Ø6.0 shank, Ø4.4 bore, 3.3 pitch, root cone to Ø8.4 at the ceiling (`IBARB_ROOT_R`). Tip at z 0, flush with the open end | Holds the intake hose (same 1/4" ID tubing). Stretched hose (~Ø10.8 at the ridges) reaches r 10.0, inside the gasket ID r 10.5 and the neck bore r 10.85. Ridges are smaller than the top barbs' Ø7.6 for that clearance; the hose only sees the media pressure drop, not pump pressure to atmosphere |
| Barbs | 3 ridges, Ø7.6 max / Ø6.0 shank, 16 tall above the plate, Ø9 collar | 1/4" ID vinyl. Ridges are wide at the bottom so tubing pushes down on |
| Grip ribs | 30 grooves r 0.9 | |
| Hook rail | web 8 wide from y 12 to 20, dovetail y 20 to 24, width 8 to 16 (45° flanks), full cap height | Same height as the cap, so it prints upright with the cap |

Print: PETG, 100% infill (or at least 5 walls), **open end down** so threads print upright. The
intake barb then stands on the bed as a free column and grows up into the ceiling; its ridges
widen upward (shallow ~10° overhang, flat tops), so no supports. The internal ceiling is a ~28 mm
bridge with the barb as a pillar (tree supports if the printer bridges poorly).

## Gasket: `bottle_filter_gasket_tpu.stl`
27.5 OD × 21 ID × 2 (`GASKET_ID_R` 10.5, `GASKET_T`). TPU 95A, or cut from silicone/EPDM sheet.
It sits on the cap ceiling and the bottle lip seals against it. **Required for pressure.**

## Intake hose (not printed)
A piece of the same 1/4" ID × 3/8" OD tubing as the feed and return hoses, pushed up onto the
intake barb. Cut it to bottle height − ~20 mm (`INTAKE_HOSE_LEN` 180 is only used by the
mockup) and cut the bottom end at an angle so it can't seal against the bottle floor.

This replaced the printed dip tube (Ø7 rigid tube with a spigot in a Ø6.5 socket) on 2026-10-11
(see 01, R7). Assembly: push the hose onto the barb, feed it down the neck, pack the media around
it, then screw the cap on. The hose turns with the cap (about 1.5 to 2 turns); loosely packed
floss lets it follow.

## Tank hook: `bottle_filter_tank_hook.stl`
The profile is in the YZ plane (`hook_profile()`), extruded `HOOK_W` 26 along X.
- Standoff block y 19.75 to 35, z 0 to 24.5, containing the dovetail slot (clearance `CLR` 0.25 per
  side). The slot is closed at the top (z 19.75 to 24.5) and open at the bottom.
- Plate against the outside glass: y 30 to 35 (`HOOK_T` 5). The glass outer face is at y 35
  (`BOTTLE_R`+2), so the bottle body clears the glass by about 2 mm.
- Bridge over the rim at z 55 to 60 (`HOOK_H` 55, the rim height above the cap's open end).
  The gap fits glass up to `GLASS_T` 12. 2 mm chamfer in the inner corner.
- Lip inside the tank: 5 thick, reaches `LIP_L` 18 down.
- Exported **lying on its side** (`lay_flat`: X becomes vertical). Layers then run along the J,
  and the 45° dovetail flanks print without support.
- Load: a 500 mL bottle full of water is about 0.6 kg. Rough bending stress at the plate is about
  5 MPa, well under PETG layer strength.

## Return clip: `bottle_filter_return_clip.stl`
The profile is in `clip_profile()`, extruded `CLIP_W` 18. Same glass frame as the hook, but the gap is
`CLIP_GLASS` (default 6, **must equal the user's glass**).
- Legs `CLIP_T` 3 thick (thin enough to flex). Outer leg `CLIP_OUT_L` 15 with a 0.6 mm
  (`CLIP_GRIP`) grip ridge. Inner leg `CLIP_IN_L` 34.
- C-ring on the tank side of the inner leg, at the bottom 16 mm of the leg. Hole Ø9.9
  (`HOSE_OD` 9.5 + 0.4). Opening 0.78 × OD ≈ 7.4 mm faces into the tank. Hose axis is vertical.
- Exported lying on its side. The hose hole is then horizontal (a 9.9 mm unsupported circle,
  usually fine).

## Flow path and hydraulics
pump → feed hose → inlet barb → intake barb → intake hose → bottle bottom → up through media → outlet
hole (top plate) → outlet barb → return hose → clip → tank, ending about 18 mm below the surface.

- The narrowest passage is the 4.4 mm bores. Fine for 150 to 300 L/h mini pumps; it limits bigger ones.
- The pump must lift about 8 to 10 cm over the rim and overcome the media. Spec: **at least 0.6 m head**.
- The bottle hangs **below the tank water line**. With the system sealed and full, a leak
  anywhere in the bottle or cap siphons the tank (even with the pump off). Hence the 24 h leak-test
  warning in PARTS_LIST.md.
- There's no outlet strainer. Fine floss/sponge is assumed; loose small media could migrate
  into the outlet.

## Mockup scene layout (`mockup/build_mockup.py`)
Rim z 55, tank 250 tall (floor z -195), water line rim − 20, glass at y 35 to 41 (uses
`CLIP_GLASS`, so the hook lip has a 6 mm gap inside), bottle height 205 (lip at z 11.5), pump
40×28×34 at x -55 against the glass, return clip at x +55, hoses arc to z ≈ 83 over the rim.
The intake hose (red) runs straight down the neck from the barb, then sags up to ~9 mm off-axis
toward −X/−Y through the media and ends 6 mm above the floor area. The media is not cut around it
(it's translucent).
