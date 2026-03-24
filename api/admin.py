from django.contrib import admin
from .models import VideoJob


@admin.register(VideoJob)
class VideoJobAdmin(admin.ModelAdmin):

    list_display = (
        "job_id",
        "job_type",
        "status",
        "stage",
        "progress",
        "created_at"
    )

    list_filter = ("job_type", "status", "created_at")

    search_fields = ("job_id", "prompt", "transcription")

    readonly_fields = (
        "job_id",
        "created_at",
        "updated_at",
        "progress"
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("Core Info", {
            "fields": ("job_id", "job_type", "status", "stage", "progress")
        }),
        ("Prompt & Text", {
            "fields": ("prompt", "transcription")
        }),
        ("Media", {
            "fields": ("input_video", "input_image", "output_video", "output_image")
        }),
        ("Debug", {
            "fields": ("error_message", "meta_data", "duration")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )