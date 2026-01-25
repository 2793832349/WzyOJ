from django.db import models

class CourseVideo(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_READY = 'ready'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_READY, 'Ready'),
        (STATUS_FAILED, 'Failed'),
    ]

    course_id = models.IntegerField(db_index=True)
    original_file = models.FileField(upload_to='course_videos/originals/')
    hls_dir = models.CharField(max_length=512, blank=True, default='')
    m3u8_url = models.CharField(max_length=1024, blank=True, default='')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'CourseVideo(id={self.id} course={self.course_id} status={self.status})'