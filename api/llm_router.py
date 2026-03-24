import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

device = "cuda" if torch.cuda.is_available() else "cpu"

model_id = "mistralai/Mistral-7B-Instruct-v0.2"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16 if device=="cuda" else torch.float32).to(device)

def run_llm(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=200)
    return tokenizer.decode(out[0], skip_special_tokens=True)

def route(prompt):
    q = f"""
    Decide task for prompt:
    {prompt}

    Options:
    image
    video
    image_edit
    video_edit
    subtitle

    Output only one word.
    """
    res = run_llm(q)
    for k in ["image","video","image_edit","video_edit","subtitle"]:
        if k in res.lower():
            return k
    return "image"