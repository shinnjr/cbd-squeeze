#!/usr/bin/env python3
"""Generate Simple Tinctures product imagery via local Flux Dev (ComfyUI API)."""
import json, urllib.request, time, sys, random

API = "http://127.0.0.1:8188"

SHOTS = {
  # name: (prompt, negative, w, h)
  "hero-bottle": (
    "professional product photography of a single amber glass dropper bottle with black cap, "
    "completely unlabeled bare amber glass bottle, no label, no sticker, no printing on a soft blush pink seamless studio backdrop, "
    "soft diffused studio lighting from left, gentle shadow, premium DTC skincare aesthetic, "
    "shallow depth of field, ultra sharp, photorealistic, no text",
    "label, sticker, text, letters, typography, watermark, writing, logo, clutter, hands, people, busy background",
    1024, 1280),
  "squeeze-lifestyle": (
    "photorealistic close-up of hands squeezing golden CBD oil concentrate from a small pouch "
    "into a glass tincture bottle on a bright kitchen counter, blush pink and cream tones, "
    "morning window light, shallow depth of field, premium lifestyle product photography, no text",
    "text, watermark, clutter, mess, dark moody lighting",
    1216, 832),
  "kitchen-flatlay": (
    "top-down flat lay photography on blush pink linen: amber glass dropper bottle, small glass "
    "jar of golden oil, brass dropper, recipe card, soft natural morning light, minimalist premium "
    "wellness aesthetic, muted pink and gold palette, photorealistic, no text",
    "text, watermark, hands, people, harsh shadows",
    1152, 896),
}

def submit(graph):
    req = urllib.request.Request(API+"/prompt", data=json.dumps({"prompt": graph}).encode(),
                                 headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())["prompt_id"]

def wait(pid):
    while True:
        time.sleep(10)
        q = json.loads(urllib.request.urlopen(API+"/queue", timeout=15).read())
        if pid not in [x[1] for x in q.get("queue_running",[])] + [x[1] for x in q.get("queue_pending",[])]:
            h = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=15).read())
            return h.get(pid, {})

def main():
    which = sys.argv[1] if len(sys.argv)>1 else None
    shots = {k:v for k,v in SHOTS.items() if not which or k==which}
    ckpt = json.loads(urllib.request.urlopen(API+"/object_info/CheckpointLoaderSimple", timeout=10).read())["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    flux = [c for c in ckpt if "juggernaut" in c.lower()][0]
    for name,(pos,neg,w,h) in shots.items():
        g = {
          "4": {"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":flux}},
          "5": {"class_type":"EmptyLatentImage","inputs":{"width":w,"height":h,"batch_size":1}},
          "6": {"class_type":"CLIPTextEncode","inputs":{"text":pos,"clip":["4",1]}},
          "7": {"class_type":"CLIPTextEncode","inputs":{"text":neg,"clip":["4",1]}},

          "3": {"class_type":"KSampler","inputs":{"seed":random.randint(1,10**9),"steps":30,"cfg":4.5,
                "sampler_name":"euler","scheduler":"simple","denoise":1,
                "model":["4",0],"positive":["6",0],"negative":["7",0],"latent_image":["5",0]}},
          "8": {"class_type":"VAEDecode","inputs":{"samples":["3",0],"vae":["4",2]}},
          "9": {"class_type":"SaveImage","inputs":{"images":["8",0],"filename_prefix":f"st_{name}"}},
        }
        pid = submit(g)
        print(f"[{name}] queued {pid}, rendering (flux on MPS takes a few min)...", flush=True)
        hist = wait(pid)
        st = hist.get("status",{})
        if str(st.get("status_str"))=="error":
            print(f"[{name}] ERROR:", json.dumps(st.get("messages",[["","?"]])[-1])[:300], flush=True)
            continue
        outs = hist.get("outputs",{})
        for node_id, o in outs.items():
            if "images" in o:
                im = o["images"][0]
                url = f"{API}/view?filename={im['filename']}&subfolder={im['subfolder']}&type={im['type']}"
                dest = f"/Users/jamesshinn/projects/cbd-squeeze/site/assets/{name}.png"
                open(dest,"wb").write(urllib.request.urlopen(url, timeout=60).read())
                import os
                print(f"[{name}] SAVED {dest} ({os.path.getsize(dest)//1024}KB)", flush=True)

if __name__ == "__main__":
    main()
