from django import forms
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from image_cropping import ImageCropField, ImageRatioField
from easy_thumbnails.files import get_thumbnailer


GENDER_CHOICES = (
    ('male', 'Masculino'),
    ('female', 'Feminino'),
    ('other', 'Outro')
)

UF_CHOICES = (
    ('AC', 'AC'),
    ('AL', 'AL'),
    ('AP', 'AP'),
    ('AM', 'AM'),
    ('BA', 'BA'),
    ('CE', 'CE'),
    ('DF', 'DF'),
    ('ES', 'ES'),
    ('GO', 'GO'),
    ('MA', 'MA'),
    ('MS', 'MS'),
    ('MT', 'MT'),
    ('MG', 'MG'),
    ('PA', 'PA'),
    ('PB', 'PB'),
    ('PR', 'PR'),
    ('PE', 'PE'),
    ('PI', 'PI'),
    ('RJ', 'RJ'),
    ('RN', 'RN'),
    ('RS', 'RS'),
    ('RO', 'RO'),
    ('RR', 'RR'),
    ('SC', 'SC'),
    ('SP', 'SP'),
    ('SE', 'SE'),
    ('TO', 'TO'),
)


def sizeof_fmt(num, suffix='B'):
    """
    Shamelessly copied from StackOverflow:
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size

    :param num:
    :param suffix:
    :return:
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def avatar_validation(image):
    if image:
        # 10 MB
        max_file_size = 10 * 1024 * 1024
        if image.size > max_file_size:
            error_message = 'The maximum file size is {0}'
            raise forms.ValidationError(
                error_message.format(sizeof_fmt(max_file_size))
            )


class UserProfile(models.Model):
    gender = models.CharField(max_length=999, choices=GENDER_CHOICES, blank=True, null=True)
    uf = models.CharField(max_length=2, choices=UF_CHOICES, null=True, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    user = models.OneToOneField("accounts.User", related_name='profile')
    avatar = ImageCropField(upload_to="avatars/", null=True, blank=True,
                            validators=[avatar_validation])
    cropping = ImageRatioField('avatar', '140x140',)

    def get_avatar_140x140(self):
        return get_thumbnailer(self.avatar).get_thumbnail({
            'size': (140, 140),
            'box': self.cropping,
            'crop': True,
            'detail': True,
        }).url


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
