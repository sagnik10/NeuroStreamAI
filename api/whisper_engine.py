import os
os.environ["PATH"] += r";C:\Users\nwp\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"

import whisper
from .translator_engine import translate

model = None


def load():

    global model

    if model is None:
        model = whisper.load_model("base")


def transcribe_and_translate(audio, lang="he"):

    load()

    res = model.transcribe(audio, fp16=False)

    out = []

    for s in res["segments"]:

        translated = translate(s["text"], tgt=lang)

        out.append({
            "start": s["start"],
            "end": s["end"],
            "text": translated
        })

    return out