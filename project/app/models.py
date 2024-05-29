from django.db import models


# Create your models here.

class Video(models.Model):

    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    hls_playlist = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
