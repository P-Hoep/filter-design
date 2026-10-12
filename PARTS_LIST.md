# Bottle Canister Filter: Parts List (non-printed)

Everything you need besides the 3D-printed parts. Sizes match the STLs in this folder.

| # | Part | Qty | Spec / what to look for | Notes |
|---|------|-----|-------------------------|-------|
| 1 | PET bottle | 1 | 500 mL to 1 L soda or water bottle, **28 mm PCO-1881 neck** (almost every current soda bottle) | Prefer a **carbonated-drink** bottle; they're rated for pressure. Body up to ~66 mm diameter clears the glass (change `BOTTLE_R` for wider ones). |
| 2 | Mini submersible pump | 1 | 3 to 6 W, about 150 to 300 L/h, **at least 0.6 m max head**, outlet nozzle for 1/4" (6 mm) ID tubing, suction-cup mount | The pump has to lift water about 10 cm over the rim and push it through the media. A pump rated near zero head will barely move water. |
| 3 | Tubing | 1.2 to 1.7 m | **1/4" ID x 3/8" OD** (6.4 x 9.5 mm) vinyl or silicone, aquarium/food-safe | Three pieces: pump to inlet, outlet to tank, and the **intake hose** inside the bottle (bottle height minus ~20 mm; cut the bottom end at an angle so it can't seal against the floor). Soft tubing is easiest to push onto the intake barb. The return clip is sized for 9.5 mm OD. |
| 4 | Filter media | to fill | Unscented polyester filter floss, coarse sponge, and/or small ceramic rings | Everything has to fit through the ~21 mm bottle neck. Floss or sponge strips are easiest. Pack it loosely: too tight cuts flow. |
| 5 | Gasket (if not printing the TPU one) | 1 | 2 mm silicone or EPDM sheet, cut to **27.5 mm OD x 21 mm ID** | Seals the bottle lip against the cap. Don't run without it. |
| 6 | PTFE (plumber's) tape | 1 roll | Standard 12 mm | Optional, for the barbs if a hose leaks. |
| 7 | Small hose clamps or zip ties | 2 to 4 | Fit 3/8" OD tubing | Optional. Keeps the hoses from creeping off the barbs under pressure. |
| 8 | Inline flow-control valve | 1 | For 1/4" ID tubing | Optional. Turns the flow down if the pump is too strong for a small tank. |

## Consumables for the printed parts
- PETG filament: about 30 g (cap, hook, return clip).
- TPU filament (95A): about 1 g (gasket), optional.

## Printed parts (for reference)
| File | Material | Orientation |
|------|----------|-------------|
| `bottle_filter_cap.stl` | PETG, 100% infill | Open end down (the intake barb tip stands on the bed) |
| `bottle_filter_tank_hook.stl` | PETG | Flat on its side, as exported |
| `bottle_filter_return_clip.stl` | PETG | Flat on its side, as exported. Set `CLIP_GLASS` to your glass thickness first. |
| `bottle_filter_gasket_tpu.stl` | TPU 95A | Flat |

## Before you leave it running
Fill and run the assembled filter over a sink or tray for 24 hours to check for drips. The bottle hangs **below the tank's water line**, so any leak in the cap, gasket or bottle can **siphon water out of the tank** even with the pump off.
