"""Blender flythrough of ../filter_mockup.glb, one camera move per narration line.

    Blender -b --python render_flythrough.py -- [preview]
Reads shots.json (camera/look-at paths in mockup mm) and timing.json (seconds per shot from
narrate.py), and renders PNG frames to frames/. "preview" renders only the first frame of each shot.
"""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, RES = 24, (1280, 720)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
preview = "preview" in args

shots = json.load(open(os.path.join(HERE, "shots.json")))
timing = json.load(open(os.path.join(HERE, "timing.json")))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, "..", "filter_mockup.glb"))
sc = bpy.context.scene
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 24
sc.render.resolution_x, sc.render.resolution_y = RES
sc.render.fps = FPS
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("world")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.42, 0.47, 0.55, 1)
bg.inputs[1].default_value = 1.0
for mat in bpy.data.materials:
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(-35))

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 32
cam.data.clip_start = 0.005
target = bpy.data.objects.new("target", None)
sc.collection.objects.link(target)
track = cam.constraints.new("TRACK_TO")
track.target, track.track_axis, track.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"


def m(p):  # mockup mm -> Blender metres (glTF import restores Z-up)
    return tuple(v / 1000 for v in p)


frame = 1
starts = []
for shot, dur in zip(shots, timing):
    n = max(2, round(dur * FPS))
    starts.append(frame)
    for f, i in ((frame, 0), (frame + n - 1, 1)):
        cam.location, target.location = m(shot["cam"][i]), m(shot["look"][i])
        cam.keyframe_insert("location", frame=f)
        target.keyframe_insert("location", frame=f)
    frame += n
sc.frame_start, sc.frame_end = 1, frame - 1

os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
if preview:
    for i, f in enumerate(starts):
        sc.frame_set(f + 12)
        sc.render.filepath = os.path.join(HERE, "frames", f"preview_{i}.png")
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = os.path.join(HERE, "frames", "f_")
    bpy.ops.render.render(animation=True)
