# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

GENDER_CHOICES = (('M', 'Homme'), ('F', 'Femme'))
SCHOOL_CHOICES = (
    ('X', 'Polytechnique'),
    ('HEC', 'HEC'),
    ('ECP', 'Centrale'),
    ('OTHER', 'Accompagnant'),
    )
YEAR_CHOICES = list((str(x), str(x)) for x in range(datetime.date.today().year - 19, 1900, -1))


def next_edition():
    return Edition.objects.next()


class EditionManager(models.Manager):
    def next(self):
        try:
            return self.filter(date__gt=datetime.date.today()).all()[0]
        except (Edition.DoesNotExist, IndexError):
            return None

    def last(self):
        try:
            return self.filter(date__lte=datetime.date.today()).latest('date')
        except Edition.DoesNotExist:
            return None


class Edition(models.Model):
    """An edition of the cross."""
    LOCATION_X = 'X'
    LOCATION_HEC = 'HEC'
    LOCATION_ECP = 'ECP'

    LOCATION_CHOICES = (
        (LOCATION_X, _(u"École polytechnique")),
        (LOCATION_HEC, _(u"HEC")),
        (LOCATION_ECP, _(u"École Centrale")),
    )

    date = models.DateField(verbose_name=_('date'), unique=True)
    close_registrations = models.DateField(verbose_name=_('registration deadline'), unique=True)
    location = models.CharField(verbose_name=_('location'), max_length=3, choices=LOCATION_CHOICES)

    objects = EditionManager()

    class Meta:
        verbose_name = _(u"edition")
        verbose_name_plural = _(u"editions")

    def __str__(self):
        return u'%s at %s' % (self.date, self.get_location_display())

class Category(models.Model):
    """Category of participants (junior...senior)"""
    name = models.CharField(_('name'), max_length=200, unique=True)
    gender = models.CharField(verbose_name=_('gender'), max_length=1, choices=GENDER_CHOICES)
    min_age = models.IntegerField(_('min_age'))

    class Meta:
        verbose_name = _(u"category")
        verbose_name_plural = _(u"categories")

    def __str__(self):
        return self.name

    @property
    def max_birth_year(self):
        return datetime.date.today().year - self.min_age


class Participant(models.Model):
    """A participant."""
    firstname = models.CharField(verbose_name=_('firstname'), max_length=200)
    lastname = models.CharField(verbose_name=_('lastname'), max_length=200)
    birthyear = models.CharField(verbose_name=_('birthyear'), max_length=4, choices=YEAR_CHOICES, blank=True,null=True)
    gender = models.CharField(verbose_name=_('gender'), max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField(verbose_name=_('email'))
    category = models.ForeignKey(Category, verbose_name=_('category'))
    school = models.CharField(verbose_name=_('school'), max_length=5, choices=SCHOOL_CHOICES)
    promo = models.IntegerField(verbose_name=_('promo'), blank=True, null=True)

    last_edition = models.ForeignKey(Edition, default=next_edition)

    def __str__(self):
        return '%s %s %s <%s> (%s %d)' % (self.gender, self.firstname, self.lastname, self.email,
            self.school, self.promo or 0)
  
