from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

class FilerVideoPluginModel(CMSPlugin):
    """A video element"""
    
    # see cmsplugin_filer_image.models.FilerImage
    title = models.CharField(
        _("title"),
        null=False,
        blank=False,
        max_length=255
    )
    
    video_file = FilerFileField(
        blank = False, null = False,
        verbose_name = _('Video file'),
        related_name = '+'
    )
    
    width = models.PositiveIntegerField(
        _("width"), null=True, blank=True,
        help_text = _("The width of the video, in CSS pixels")
    )
    
    height = models.PositiveIntegerField(
        _("height"), null=True, blank=True,
        help_text = _("The height of the video, in CSS pixels")
    )
    
    autoplay = models.BooleanField(
        _("play automatically"),
        default = False,
        help_text = _("Automatically begin playback of the video as soon as it can do so without stopping")
    )
    
    controls = models.BooleanField(
        _("show controls"),
        default = False,
        help_text = _("Expose a user interface for controlling playback of the video")
    )
    
    loop = models.BooleanField(
        _("loop"),
        default = False,
        help_text = _("Seek back to the start of the video upon reaching the end")
    )
    
    poster = FilerImageField(
        blank = True, null = True,
        verbose_name = _("poster image"),
        help_text = _("An image to show while no video data is available"),
        related_name = '+'
    )
    
    muted = models.BooleanField(
        _("muted"),
        default = False,
        help_text = _("Mute the video soundtrack")
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Self hosted video")
        verbose_name_plural = _("Self hosted videos")
