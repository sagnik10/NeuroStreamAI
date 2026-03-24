import torch
import uuid
import os
import imageio
import numpy as np
import cv2

device = "cuda" if torch.cuda.is_available() else "cpu"

BASE_MEDIA = "media"
OUTPUT_DIR = os.path.join(BASE_MEDIA, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sd_pipe = None
llm_model = None
llm_tokenizer = None


def load_sd():
    global sd_pipe
    if sd_pipe is not None:
        return

    from diffusers import StableDiffusionPipeline

    sd_pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )

    sd_pipe.safety_checker = None
    sd_pipe.requires_safety_checker = False

    if device == "cuda":
        sd_pipe.to("cuda")
        sd_pipe.enable_attention_slicing()
        sd_pipe.enable_vae_slicing()
    else:
        sd_pipe.to("cpu")


def load_llm():
    global llm_model, llm_tokenizer
    if llm_model is not None:
        return

    from transformers import AutoTokenizer, AutoModelForCausalLM

    llm_tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    llm_model = AutoModelForCausalLM.from_pretrained("distilgpt2").to(device)


def refine_prompt(prompt):
    load_llm()
    inputs = llm_tokenizer(prompt, return_tensors="pt").to(device)
    out = llm_model.generate(**inputs, max_new_tokens=20)
    return llm_tokenizer.decode(out[0], skip_special_tokens=True)


def route_intent(text):
    t = text.lower()
    if "video" in t or "animation" in t or "cinematic" in t:
        return "video"
    return "image"


def generate_image(prompt):
    load_sd()
    img = sd_pipe(prompt, num_inference_steps=25, guidance_scale=7.5).images[0]
    path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.png")
    img.save(path)
    return path.replace("\\", "/")


def generate_video(prompt):
    load_sd()

    frames = []

    for i in range(12):
        generator = torch.Generator(device=device).manual_seed(i)
        img = sd_pipe(
            prompt,
            num_inference_steps=20,
            guidance_scale=7.5,
            generator=generator
        ).images[0]

        frame = np.array(img)
        frame = cv2.GaussianBlur(frame, (3, 3), 0)
        frames.append(frame)

    smooth_frames = []
    for i in range(len(frames) - 1):
        f1 = frames[i]
        f2 = frames[i + 1]

        for j in range(4):
            alpha = j / 4.0
            blended = cv2.addWeighted(f1, 1 - alpha, f2, alpha, 0)
            smooth_frames.append(blended)

    path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")

    imageio.mimsave(path, smooth_frames, fps=16)

    return path.replace("\\", "/")


def run_pipeline(prompt, input_path=None):
    refined = refine_prompt(prompt)
    intent = route_intent(refined)

    if intent == "video":
        output = generate_video(refined)
    else:
        output = generate_image(refined)

    return {"output": output}