import os
import uuid
import torch
import subprocess
from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

sd = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5").to(device)
vd = StableVideoDiffusionPipeline.from_pretrained("stabilityai/stable-video-diffusion-img2vid").to(device)

def save_video(frames, path):
    tmp = f"media/tmp/{uuid.uuid4()}"
    os.makedirs(tmp, exist_ok=True)
    for i,f in enumerate(frames):
        f.save(f"{tmp}/{i}.png")
    subprocess.run([
        "ffmpeg","-y","-framerate","8","-i",f"{tmp}/%d.png",
        "-c:v","libx264","-pix_fmt","yuv420p",path
    ])

def generate_image(prompt):
    img = sd(prompt).images[0]
    path = f"media/outputs/{uuid.uuid4()}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path

def generate_video(prompt):
    img = sd(prompt).images[0]
    frames = vd(img).frames
    path = f"media/outputs/{uuid.uuid4()}.mp4"
    save_video(frames, path)
    return path

def edit_image(path, prompt):
    img = Image.open(path)
    new = sd(prompt, image=img).images[0]
    out = f"media/outputs/{uuid.uuid4()}.png"
    new.save(out)
    return out

def edit_video(path):
    out = f"media/outputs/{uuid.uuid4()}.mp4"
    subprocess.run([
        "ffmpeg","-i",path,"-vf","hue=s=0","-c:a","copy",out
    ])
    return out