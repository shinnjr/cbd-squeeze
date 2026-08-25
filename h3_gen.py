#!/usr/bin/env python3
"""Generate one MiniMax H3 T2V test clip via local ComfyUI API (768p, 4-step turbo, ~5s, native audio)."""
import json, urllib.request, urllib.error, sys, time

API = "http://127.0.0.1:8188"

PROMPT = (
    "Product hero shot: a large amber glass bottle of golden CBD oil stands on a clean white "
    "kitchen counter in soft morning window light. The camera slowly orbits the bottle as golden "
    "light refracts through the liquid. A hand enters frame and squeezes a dropper, releasing one "
    "glistening drop that catches the light in slow motion. Shallow depth of field, warm tones, "
    "premium commercial look. Audio: calm ambient kitchen atmosphere, single soft water-like plink "
    "when the drop lands."
)

graph = {
    "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
    "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
    "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
    "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
    "5": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "strength_model": 1.0}},
    "6": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
        "clip": ["2", 0], "vae": ["3", 0], "prompt": PROMPT,
        "width": 832, "height": 480, "length": 124}},
    "7": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
    "8": {"class_type": "RandomNoise", "inputs": {"noise_seed": 20260825}},
    "9": {"class_type": "BasicScheduler", "inputs": {"model": ["5", 0], "scheduler": "simple", "steps": 4, "denoise": 1.0}},
    "10": {"class_type": "BasicGuider", "inputs": {"model": ["5", 0], "conditioning": ["6", 0]}},
    "11": {"class_type": "SamplerCustomAdvanced", "inputs": {
        "noise": ["8", 0], "guider": ["10", 0], "sampler": ["7", 0],
        "sigmas": ["9", 0], "latent_image": ["6", 1]}},
    "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
    "13": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}},
    "14": {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24.0}},
    "15": {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": "H3/test_t2v", "format": "auto", "codec": "auto"}},
}

req = urllib.request.Request(API + "/prompt",
    data=json.dumps({"prompt": graph, "client_id": "hermes-h3"}).encode(),
    headers={"Content-Type": "application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=60).read())
pid = r["prompt_id"]
print("queued:", pid)

t0 = time.time()
while True:
    time.sleep(15)
    try:
        h = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=20).read())
        if pid in h:
            st = h[pid].get("status", {})
            print(f"done in {int(time.time()-t0)}s | status={st.get('status_str')}")
            for node_out in h[pid].get("outputs", {}).values():
                for k, v in node_out.items():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and ("filename" in item or "subfolder" in item):
                                print("OUTPUT:", item)
            break
    except urllib.error.URLError:
        pass
    if time.time() - t0 > 3600:
        print("TIMEOUT after 60m"); sys.exit(1)
