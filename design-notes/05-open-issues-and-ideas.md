# 05: Open Issues, Risks and Ideas

## Risks / known limitations
1. **Thread fit is unproven.** If it's too tight or loose, adjust `R_BORE`/`R_CREST` (radial) or
   `TOOTH_ROOT_W`/`TOOTH_CREST_W` (axial) in steps of 0.1 to 0.2 mm. Older bottles with the
   taller **PCO-1810** neck have the same thread and will probably still fit; the skirt length was kept short.
2. **Siphon / leak hazard.** The bottle hangs below the water line, so any leak drains the tank down
   to the leak height, pump on or off. A check valve won't stop it (the flow goes the same
   direction as normal). Mitigations: a leak test, a tray under the bottle, or mounting the bottle
   above the water line (needs a longer `HOOK_H`/hook redesign).
3. **The mockup glass is 6 mm (`CLIP_GLASS`) but the hook gap is 12 (`GLASS_T`).** That's
   intentional (the hook fits up to 12, the clip must match exactly), but the hook lip sits 6 mm
   off the inner glass in renders.
4. **No outlet strainer.** Small loose media could be pushed into the outlet. A slotted
   strainer cup on the cap underside would need supports (it hangs from the ceiling when
   printed open-end-down). Alternatively, a separate push-in strainer part.
5. **Flow restriction.** 4.4 mm bores are fine for mini pumps. For bigger pumps, enlarge the barbs
   and bores (5/16" or 3/8" tubing); `PORT_X` would need revisiting, since the ports are already close to the neck bore.
6. **The dip tube is tall and thin.** Printing can wobble. The 1/4" OD rigid tube alternative is in the BOM.
7. **Hook in the mockup is at y=+side and the pump at x=-55.** The real install can mirror this; only the
   clip and hook positions along the rim are free.
8. `bottle_filter_assembly_preview.png` predates the return clip and the final colours.
9. `mockup/README.md` lists the video at `video/filter_flythrough.mp4`, but the user moved it to
   the repo root.
10. **GitHub README video:** GitHub does not render `<video>` or a relative `.mp4` from the repo as an inline
    player. It only does that for files uploaded via the web editor (`github.com/user-attachments/...`, ≤10 MB
    on free plans). So the README shows a GIF teaser linking to `media/filter_flythrough_480p.mp4`.
    For an inline player, the user can drag the 480p MP4 into the README editor on github.com.
    Rebuild the media files with:
    `ffmpeg -i filter_flythrough.mp4 -map 0:v -map 0:a -map '0:s?' -vf scale=854:-2 -c:v libx264 -crf 30 -preset slow -c:a aac -b:a 64k -c:s mov_text -movflags +faststart media/filter_flythrough_480p.mp4`
    and, for the GIF, `select` three ranges, then `setpts=N/(24*TB)` (use the *source* fps or it plays in slow motion), `fps=10`, `scale=560`,
    then palettegen/paletteuse. Quote `'0:s?'` in zsh.
11. The `build_filter_cap.py` docstring says the solid is built "from the dimensions in the DXF".
    It's actually the other way round: the script is the source of truth and the DXF documents it.

## Likely next requests (and how to approach them)
- **"Make it fit a different bottle"**: change the thread constants. For 38 mm necks or jars,
  rewrite the thread parameters and scale `R_OUT`/`H_SKIRT`, and re-verify handedness.
- **"Bigger hoses / different tubing"**: barb profile in `barb()` (radii 3.0/3.8, collar 4.5),
  `R_HOLE`, `HOSE_OD`, and `HOSE_SNAP` for the clip.
- **"Different tank"**: `GLASS_T` (hook), `CLIP_GLASS` (clip), `HOOK_H` (cap height below the
  rim), `BOTTLE_R` (bottle standoff). For framed tanks with a plastic rim lip, the hook bridge may
  need a deeper gap or a notch.
- **"Add a valve / flow control / quick disconnect"**: easiest as inline bought parts (BOM item 9).
- **"Pre-filter on the pump intake"**: a printed sponge cage that pushes onto the pump intake. Use
  the pump stand-in dimensions in `build_mockup.py` as a placeholder, and ask for the real pump model.
- **"Update the video"**: edit `shots.json` (text and camera paths). Re-run narrate → preview render
  → full render → make_video (03). If only the text changes, the camera timing re-flows automatically.
- **"Commit / push"**: only when asked. Remote `P-Hoep/filter-design`, branch `main`. STLs and
  the MP4 are binary (~14 MB cap STL, ~7 MB MP4); consider Git LFS if the repo grows.
