"""Assemble the flythrough: rendered frames + Kokoro narration + captions -> filter_flythrough.mp4.

Captions are burned in (Pillow images overlaid by ffmpeg, so no libass/drawtext needed) and also
embedded as a soft subtitle track. Run after narrate.py and render_flythrough.py.
"""
import json
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, W, H = 24, 1280, 720
FONT = "/System/Library/Fonts/Helvetica.ttc"

shots = json.load(open(os.path.join(HERE, "shots.json")))
timing = json.load(open(os.path.join(HERE, "timing.json")))
# match the renderer: each shot is round(duration * FPS) frames
frames = [max(2, round(d * FPS)) for d in timing]
starts = [sum(frames[:i]) / FPS for i in range(len(frames))]
ends = [s + n / FPS for s, n in zip(starts, frames)]
total = ends[-1]

cap_dir = os.path.join(HERE, "captions")
os.makedirs(cap_dir, exist_ok=True)
font = ImageFont.truetype(FONT, 30)
caps = []
for i, s in enumerate(shots):
    lines = textwrap.wrap(s["text"], 70)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lh = 40
    box_h = lh * len(lines) + 24
    d.rounded_rectangle((60, H - box_h - 30, W - 60, H - 30), 14, fill=(0, 0, 0, 150))
    for j, line in enumerate(lines):
        tw = d.textlength(line, font=font)
        d.text(((W - tw) / 2, H - box_h - 30 + 12 + j * lh), line, font=font, fill=(255, 255, 255, 255))
    path = os.path.join(cap_dir, f"cap_{i}.png")
    img.save(path)
    caps.append(path)


def ts(t):
    h, rem = divmod(t, 3600)
    m, sec = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{sec:06.3f}".replace(".", ",")


srt = os.path.join(HERE, "filter_flythrough.srt")
with open(srt, "w") as f:
    for i, s in enumerate(shots):
        f.write(f"{i + 1}\n{ts(starts[i] + 0.3)} --> {ts(ends[i] - 0.4)}\n{s['text']}\n\n")

cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(HERE, "frames", "f_%04d.png"),
       "-i", os.path.join(HERE, "narration.wav")]
for c in caps:
    cmd += ["-i", c]
cmd += ["-i", srt]
chain, prev = [], "[0:v]"
for i in range(len(caps)):
    out = f"[v{i}]"
    chain.append(f"{prev}[{i + 2}:v]overlay=0:0:enable='between(t,{starts[i]:.3f},{ends[i] - 0.05:.3f})'{out}")
    prev = out
chain.append(f"{prev}fade=t=in:st=0:d=0.6,fade=t=out:st={total - 0.8:.3f}:d=0.8,format=yuv420p[vout]")
cmd += ["-filter_complex", ";".join(chain), "-map", "[vout]", "-map", "1:a", "-map", f"{len(caps) + 2}:s",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "160k",
        "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-shortest", "-movflags", "+faststart",
        os.path.join(HERE, "filter_flythrough.mp4")]
subprocess.run(cmd, check=True)
print("wrote filter_flythrough.mp4", round(total, 1), "s")
