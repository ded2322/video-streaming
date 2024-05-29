import os
import subprocess
import logging
from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import VideoForm
from .models import Video

logger = logging.getLogger(__name__)


def convert_to_hls(input_path, output_dir) -> bool:
    try:
        # Путь к ffmpeg полный путь
        ffmpeg_path = r'C:\ffmpeg\ffmpeg.exe'

        # Создание директории, если она не существует
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Путь к выходному HLS плейлисту
        output_path = os.path.join(output_dir, 'index.m3u8')

        # Формирование команды FFmpeg для конвертации видео в HLS
        command = [
            ffmpeg_path, '-i', input_path,
            '-codec', 'copy',
            '-start_number', '0',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-f', 'hls',
            output_path,
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts')
        ]

        subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"Видео успешно конвертировано и сохранено")
        return True
    except (subprocess.CalledProcessError, Exception) as e:
        if isinstance(e, subprocess.CalledProcessError):
            logger.error(f"Ошибка при конвертации видео: {e.stderr.decode()}")
            return False
        if isinstance(e, Exception):
            logger.error(f"Неожиданная ошибка: {e}")
            return False


class UploadVideoView(View):
    def get(self, request):
        form = VideoForm()
        return render(request, 'upload_video.html', {'form': form})

    def post(self, request):
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            try:
                self._process_video(video, request)
                return redirect('video_list')
            except Exception as e:
                logger.error(f"Error in UploadVideoView, post: {str(e)}")
                return HttpResponse(f"Ошибка при попытки конвертации {str(e)}")

    def _process_video(self, video, request):
        input_file_path = video.video_file.path
        # file_path example: /media/hls/video_id
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id))
        print(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        if convert_to_hls(input_file_path, output_dir):
            hls_path = os.path.join('media', 'hls', str(video.id), 'index.m3u8')
            hls_path = hls_path.replace("\\", "/")
            full_path = request.build_absolute_uri('/' + hls_path)
            video.hls_playlist = full_path
            video.save()


class VideoListView(View):
    def get(self, request):
        videos = Video.objects.all()
        return render(request, 'video_list.html', {'videos': videos})
