from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.

class Mystery(models.Model):
    JOYFUL = 'joyful'
    LUMINOUS = 'luminous'
    SORROWFUL = 'sorrowful'
    GLORIOUS = 'glorious'
    GROUPS = {
        JOYFUL: _("Joyful Mystery"),
        LUMINOUS: _("Luminous Mystery"),
        SORROWFUL: _("Sorrowful Mystery"),
        GLORIOUS: _("Glorious Mystery"),
    }
    title = models.CharField(max_length=200, unique=True)
    group = models.CharField(max_length=15, choices=GROUPS.items())
    number = models.SmallIntegerField(unique=True)
    image_path = models.ImageField()
    quote = models.TextField()
    meditation = models.TextField()

    def number_group(self, full=True):
        number_in_group = ((self.number - 1) % 5) + 1
        if number_in_group < 4:
            seq = 'I' * number_in_group
        elif number_in_group < 5:
            seq = 'IV'
        else:
            seq = 'V'
        group_name = Mystery.GROUPS[self.group]
        if not full:
            group_name = "".join([x[0] for x in group_name.split()])
        return seq + ' ' + group_name

    def short_number_group(self):
        return self.number_group(full=False)

    def __unicode__(self):
        return self.number_group() + " " + self.title


class Intension(models.Model):
    start_date = models.DateField(unique=True)
    end_date = models.DateField(unique=True)
    universal_intension = models.TextField(max_length=2047)
    evangelisation_intension = models.TextField(max_length=2047)
    pcm_intension = models.TextField(max_length=2047)
    message = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return str(self.start_date) + " - " + str(self.end_date)


class Person(models.Model):
    name = models.CharField(max_length=127)
    email = models.EmailField(unique=True)
    active = models.BooleanField(null=False, default=True)

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
