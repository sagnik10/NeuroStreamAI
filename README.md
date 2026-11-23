<!-- SAGNIK10-STYLE-HEADER -->
<div align="center">
  <a href="https://github.com/sagnik10"><img src="https://img.shields.io/badge/Sagnik_Sen-AI%20%26%20Multimodal-275cce?style=flat-square" alt="Category" /></a>
  <img src="https://img.shields.io/badge/Stack-Python-192a43?style=flat-square" alt="Stack" />
  <img src="https://img.shields.io/badge/License-MIT-54647a?style=flat-square" alt="License" />
</div>

<p align="center">
  <a href="https://sagnik10.github.io/SagnikSenPortfolio/">Portfolio</a> ·
  <a href="https://github.com/sagnik10">GitHub Profile</a> ·
  <a href="https://github.com/sagnik10/sagnik-sen-antigravity-plugin">Antigravity Plugin</a>
</p>

---
<!-- /SAGNIK10-STYLE-HEADER -->
# NeuroStreamAI

NeuroStreamAI is a modular multimodal AI backend designed for processing and generating rich media content across text, audio, and video. It combines speech recognition, translation, subtitle generation, and generative media pipelines into a single unified system.

---

## Features

* Speech-to-text transcription using Whisper
* Multilingual translation using transformer-based models
* Automatic subtitle generation with timing optimization
* Character-per-second (CPS) control and smart text wrapping
* Prompt-based image generation using Stable Diffusion
* Prompt-based video generation via frame synthesis
* LLM-based intent routing (image vs video tasks)
* Asynchronous job processing with progress tracking
* REST API built with Django

---

## Architecture

* **ASR Engine**: Whisper-based transcription
* **Translation Engine**: NLLB / MarianMT models
* **Subtitle Processor**: Block merging, CPS enforcement, SRT generation
* **Multimodal Engine**: Image & video generation via diffusion models
* **LLM Router**: Task classification and prompt refinement
* **Backend API**: Django + DRF with threaded job execution

---

## Project Structure

```
backend/
│
├── api/
├── config/
├── templates/
├── media/
├── venv/
├── manage.py
├── requirements.txt
└── db.sqlite3
```

---

## Installation

```bash
git clone https://github.com/sagnik10/NeuroStreamAI.git
cd NeuroStreamAI/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run Server

```bash
python manage.py runserver
```

---

## API Endpoints

### Upload Video for Subtitles

```
POST /upload/
```

### AI Prompt Pipeline (Image/Video Generation)

```
POST /ai/
```

### Job Status

```
GET /status/<job_id>/
```

---

## Workflow

1. Upload video or send prompt
2. Backend creates async job
3. Pipeline processes:

   * Audio extraction
   * Transcription
   * Translation
   * Subtitle generation or media generation
4. Output stored and accessible via job status

---

## Tech Stack

* Python
* Django / Django REST Framework
* PyTorch
* Whisper
* Hugging Face Transformers
* Stable Diffusion (Diffusers)
* FFmpeg

---

## Notes

* Ensure FFmpeg is installed and added to system PATH
* GPU is recommended for faster inference
* Large model files are excluded via `.gitignore`

---

## License

MIT License


<!-- SAGNIK10-STYLE-FOOTER -->
---
<p align="center">
  Maintained by <a href="https://github.com/sagnik10"><strong>Sagnik Sen</strong></a> ·
  <a href="https://sagnik10.github.io/SagnikSenPortfolio/">Portfolio &amp; 1-on-1 Teaching</a> ·
  <a href="https://www.linkedin.com/in/sagnik-sen-0a70431a8/">LinkedIn</a>
</p>
<!-- /SAGNIK10-STYLE-FOOTER -->