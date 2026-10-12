"""Generate narration clips with Kokoro (kokoro-onnx) and record their durations in timing.json."""
import json, os, sys
import numpy as np, soundfile as sf

# kokoro-onnx's bundled espeak can't find its data on macOS; use Homebrew's espeak-ng
os.environ.setdefault("ESPEAK_DATA_PATH", "/opt/homebrew/share/espeak-ng-data")
from kokoro_onnx import Kokoro

MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/leroy-ant/pixa-video/models"))
VOICE, SPEED, GAP = "af_heart", 1.0, 0.7   # GAP: silence after each line (s)
here = os.path.dirname(os.path.abspath(__file__))
k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
shots = json.load(open(os.path.join(here, "shots.json")))
audio, timing, sr = [], [], 24000
for i, s in enumerate(shots):
    samples, sr = k.create(s["text"], voice=VOICE, speed=SPEED, lang="en-us")
    lead = np.zeros(int(0.3 * sr), dtype=np.float32)
    clip = np.concatenate([lead, samples.astype(np.float32), np.zeros(int(GAP * sr), dtype=np.float32)])
    timing.append(len(clip) / sr)
    audio.append(clip)
    print(f"shot {i}: {timing[-1]:.2f}s")
sf.write(os.path.join(here, "narration.wav"), np.concatenate(audio), sr)
json.dump(timing, open(os.path.join(here, "timing.json"), "w"))
print("total", round(sum(timing), 1), "s")
