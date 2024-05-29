from django.urls import path
from .views import VideoListView, UploadVideoView

urlpatterns = [
    path('upload/',UploadVideoView.as_view(), name='upload_video'),
    path('', VideoListView.as_view(), name='video_list'),
]