from django.db import models


class VideoJob(models.Model):

    JOB_TYPES = [
        ("subtitle", "Subtitle"),
        ("ai_image", "AI Image"),
        ("ai_video", "AI Video"),
        ("image_edit", "Image Edit"),
        ("video_edit", "Video Edit"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("error", "Error"),
    ]

    job_id = models.CharField(max_length=100, unique=True)

    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="subtitle")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stage = models.CharField(max_length=50, blank=True)

    progress = models.IntegerField(default=0)

    prompt = models.TextField(blank=True)

    transcription = models.TextField(blank=True)

    input_video = models.FileField(upload_to="uploads/", null=True, blank=True)
    input_image = models.FileField(upload_to="inputs/", null=True, blank=True)

    output_video = models.FileField(upload_to="outputs/", null=True, blank=True)
    output_image = models.FileField(upload_to="outputs/", null=True, blank=True)

    video_url = models.TextField(blank=True)

    error_message = models.TextField(blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    duration = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} ({self.job_type})"