from django.db import models

CHAPTER_TYPES = ('video', 'audio')

class MediaFileChapter(models.Model):
    media_file = models.ForeignKey('medialibrary.MediaFile', limit_choices_to = {'type__in': CHAPTER_TYPES})
    title = models.CharField(max_length=255)
    timecode = models.TimeField(help_text='hh:mm:ss')
    preview = models.ImageField(upload_to='medialibrary/section/', null=True, blank=True)

    class Meta:
        app_label = 'medialibrary'
        ordering = ('timecode',)

    def __unicode__(self):
        return self.title

    @property
    def seconds(self):
        return self.timecode.hour*3600+self.timecode.minute*60+self.timecode.second
