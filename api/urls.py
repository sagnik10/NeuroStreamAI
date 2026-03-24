from django.urls import path
from .views import home, UploadVideoView, StatusView, PromptPipelineView

urlpatterns = [
    path("", home),
    path("upload/", UploadVideoView.as_view()),
    path("ai/", PromptPipelineView.as_view()),
    path("status/<str:job_id>/", StatusView.as_view()),
]