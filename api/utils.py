import subprocess
import re

FFMPEG_PATH = r"C:\Users\nwp\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

RTL_MARK = "\u202B"
RTL_END = "\u202C"

def extract_audio(video_path, audio_path):
    subprocess.run([
        FFMPEG_PATH,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ], check=True)

def visible_len(text):
    return len(text)

def cps(text, start, end):
    dur = max(end - start, 0.1)
    return len(text) / dur

def best_split(words, max_chars):
    best = None
    score = 9999
    for i in range(1, len(words)):
        l = " ".join(words[:i])
        r = " ".join(words[i:])
        if len(l) > max_chars or len(r) > max_chars:
            continue
        s = abs(len(l) - len(r))
        if s < score:
            best = (l, r)
            score = s
    return best

def wrap_text(text, max_chars=42):
    words = text.split()
    if len(text) <= max_chars:
        return [text]
    split = best_split(words, max_chars)
    if split:
        return [split[0], split[1]]
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > max_chars:
            cur.pop()
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines[:2]

def merge_short_blocks(blocks, min_chars=12):
    merged = []
    buf = None
    for b in blocks:
        if buf is None:
            buf = b
            continue
        if len(buf["text"]) < min_chars:
            buf["text"] += " " + b["text"]
            buf["end"] = b["end"]
        else:
            merged.append(buf)
            buf = b
    if buf:
        merged.append(buf)
    return merged

def enforce_cps(blocks, max_cps=20):
    out = []
    for b in blocks:
        if cps(b["text"], b["start"], b["end"]) > max_cps:
            w = b["text"].split()
            mid = len(w) // 2
            t = (b["start"] + b["end"]) / 2
            out.append({"start": b["start"], "end": t, "text": " ".join(w[:mid])})
            out.append({"start": t, "end": b["end"], "text": " ".join(w[mid:])})
        else:
            out.append(b)
    return out

def build_word_blocks(segs):
    return [{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in segs]

def fix_punctuation(text):
    return re.sub(r"\s+([.,!?])", r"\1", text)

def fix_hebrew(text):
    words = text.split()
    fixed = []
    for w in words:
        if len(w) == 1:
            fixed.append(w)
        else:
            fixed.append(w[::-1])
    return RTL_MARK + " ".join(fixed) + RTL_END

def convert_to_srt(blocks, max_chars=42, lang="en"):
    entries = []
    for i, b in enumerate(blocks, 1):
        txt = fix_punctuation(b["text"])
        lines = wrap_text(txt, max_chars)
        text = "\n".join(lines)
        if lang == "he":
            text = fix_hebrew(text)
        entries.append({
            "index": i,
            "start": b["start"],
            "end": b["end"],
            "text": text
        })
    return entries