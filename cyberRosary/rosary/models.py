from __future__ import unicode_literals
from django.utils.translation import ugettext as _

from django.db import models
import uuid


# Create your models here.

class Mystery(models.Model):
    JOYFUL = 'joyful'
    LUMINOUS = 'luminous'
    SORROWFUL = 'sorrowful'
    GLORIOUS = 'glorious'
    GROUPS = (
        (JOYFUL, _("Joyful Mysteries")),
        (LUMINOUS, _("Luminous Mysteries")),
        (SORROWFUL, _("Sorrowful Mysteries")),
        (GLORIOUS, _("Glorious Mysteries")))
    title = models.CharField(max_length=200, unique=True)
    group = models.CharField(max_length=15, choices=GROUPS)
    number = models.SmallIntegerField(unique=True)
    image_path = models.ImageField()
    quote = models.TextField()
    meditation = models.TextField()

    def __unicode__(self):
        return self.title


class Intension(models.Model):
    start_date = models.DateField(unique=True)
    universal_intension = models.CharField(max_length=2047)
    evangelisation_intension = models.CharField(max_length=2047)
    pcm_intension = models.CharField(max_length=2047)
    message = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return str(self.start_date)


class Person(models.Model):
    name = models.CharField(max_length=127)
    email = models.EmailField(unique=True)

    def __unicode__(self):
        return self.name


class PersonIntension(models.Model):
    person = models.ForeignKey(Person)
    intension = models.ForeignKey(Intension)
    mystery = models.ForeignKey(Mystery)
    downloaded = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=63, unique=True)

    def save(self):
        if self.pk is None:
            self.code = str(uuid.uuid4())
        super(PersonIntension, self).save()


    def __unicode__(self):
        return self.code
