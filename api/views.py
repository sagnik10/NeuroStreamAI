import os
import uuid
import threading
import subprocess
import shutil

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView

from .models import VideoJob
from .utils import extract_audio, build_word_blocks, merge_short_blocks, enforce_cps, convert_to_srt
from .whisper_engine import transcribe_and_translate
from .multimodal_engine import run_pipeline

FFMPEG_PATH = r"C:\Users\nwp\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"


def home(request):
    return render(request, "index.html")


class UploadVideoView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        video = request.FILES["file"]
        lang = request.data.get("language", "en")

        job_id = str(uuid.uuid4())

        job = VideoJob.objects.create(
            job_id=job_id,
            job_type="subtitle",
            status="processing",
            stage="uploading",
            progress=0,
            input_video=video
        )

        video_path = job.input_video.path

        threading.Thread(
            target=process_video,
            args=(job_id, video_path, lang),
            daemon=True
        ).start()

        return JsonResponse({"job_id": job_id})


class StatusView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, job_id):
        try:
            job = VideoJob.objects.get(job_id=job_id)

            return JsonResponse({
                "status": job.status,
                "stage": job.stage,
                "progress": job.progress,
                "video_url": job.output_video.url if job.output_video else "",
                "image_url": job.output_image.url if job.output_image else "",
                "error": job.error_message
            })

        except VideoJob.DoesNotExist:
            return JsonResponse({"error": "Invalid job id"}, status=404)


class PromptPipelineView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        prompt = request.data.get("prompt")
        file = request.FILES.get("file")

        job_id = str(uuid.uuid4())

        job = VideoJob.objects.create(
            job_id=job_id,
            job_type="ai",
            status="processing",
            stage="queued",
            progress=0,
            prompt=prompt
        )

        input_path = None

        if file:
            input_dir = os.path.join(settings.MEDIA_ROOT, "inputs")
            os.makedirs(input_dir, exist_ok=True)

            filename = f"{uuid.uuid4()}_{file.name}"
            input_path = os.path.join(input_dir, filename)

            with open(input_path, "wb") as f:
                for chunk in file.chunks():
                    f.write(chunk)

        threading.Thread(
            target=process_ai_job,
            args=(job_id, prompt, input_path),
            daemon=True
        ).start()

        return JsonResponse({"job_id": job_id})


def process_ai_job(job_id, prompt, input_path):

    try:
        job = VideoJob.objects.get(job_id=job_id)

        job.stage = "running_ai"
        job.progress = 20
        job.save(update_fields=["stage", "progress"])

        result = run_pipeline(prompt, input_path)
        output = result.get("output")

        if output.endswith(".png"):
            job.output_image.name = output.replace("media/", "")
        else:
            job.output_video.name = output.replace("media/", "")

        job.status = "completed"
        job.stage = "done"
        job.progress = 100

        job.save(update_fields=[
            "status",
            "stage",
            "progress",
            "output_image",
            "output_video"
        ])

    except Exception as e:
        job = VideoJob.objects.get(job_id=job_id)
        job.status = "error"
        job.stage = "failed"
        job.error_message = str(e)
        job.save(update_fields=["status", "stage", "error_message"])


def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}".replace(".", ",")


def process_video(job_id, video_path, lang):

    try:
        job = VideoJob.objects.get(job_id=job_id)

        job.stage = "extracting_audio"
        job.progress = 10
        job.save(update_fields=["stage", "progress"])

        audio_path = os.path.join(settings.MEDIA_ROOT, f"{uuid.uuid4()}.wav")

        extract_audio(video_path, audio_path)

        job.stage = "transcribing"
        job.progress = 25
        job.save(update_fields=["stage", "progress"])

        segments = transcribe_and_translate(audio_path, lang)

        blocks = build_word_blocks(segments)
        blocks = merge_short_blocks(blocks)
        blocks = enforce_cps(blocks)

        temp_dir = os.path.dirname(video_path)

        srt_path = os.path.join(temp_dir, f"{uuid.uuid4()}.srt")

        entries = convert_to_srt(blocks, lang=lang)

        with open(srt_path, "w", encoding="utf-8") as srt:
            for e in entries:
                srt.write(f"{e['index']}\n")
                srt.write(f"{format_time(e['start'])} --> {format_time(e['end'])}\n")
                srt.write(f"{e['text']}\n\n")

        job.stage = "rendering_video"
        job.progress = 80
        job.save(update_fields=["stage", "progress"])

        output_video = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, "outputs", output_video)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        video_name = os.path.basename(video_path)
        srt_name = os.path.basename(srt_path)
        output_name = os.path.basename(output_path)

        subprocess.run([
            FFMPEG_PATH,
            "-y",
            "-i", video_name,
            "-vf", f"subtitles={srt_name}",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "copy",
            output_name
        ],
        cwd=temp_dir,
        check=True)

        final_output_path = os.path.join(settings.MEDIA_ROOT, "outputs", output_video)

        shutil.move(
            os.path.join(temp_dir, output_name),
            final_output_path
        )

        job.output_video.name = "outputs/" + output_video
        job.status = "completed"
        job.stage = "done"
        job.progress = 100

        job.save(update_fields=[
            "output_video",
            "status",
            "stage",
            "progress"
        ])

    except Exception as e:
        job = VideoJob.objects.get(job_id=job_id)
        job.status = "error"
        job.stage = "failed"
        job.error_message = str(e)
        job.save(update_fields=["status", "stage", "error_message"])