from django.db import models


class SliderManager(models.Manager):
    """
        Manager for Slider class
    """
    def activated(self):
        """
            return only activated sliders
        """
        return self.filter(is_active=True)
