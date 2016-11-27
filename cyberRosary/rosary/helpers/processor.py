#!/usr/bin/python
from django.utils.translation import ugettext as _
from django.utils.datetime_safe import datetime

from cyberRosary import settings


def find_recent_intensions(count):
    # todo configure start date
    today = datetime.today()
    recent_intensions = Intension.objects.filter(start_date__lte=today).order_by('-start_date')[:count]
    return recent_intensions


def find_person_itnensions(current_intension):
    # todo: optimise query if needed - join and eager person, mystery
    person_intensions = PersonIntension.objects.filter(intension=current_intension)
    return person_intensions


def notify_not_downloaded(person_intensions, subject_ext=""):
    logger.info("Notyfying not downloaded.")
    for pi in person_intensions:
        if pi.person.active and not pi.downloaded:
            code = settings.LOCATION_TEMPLATE % pi.code
            email = pi.person.email
            message = _(
                "God bless,\n Under the link \n%s\nthere is a new Live Rosary mystery.\n Pease report any problems with downloading or opening the file to rosary@cyberarche.pl email address.\nSincerely\nCyberarche Team") % code
            # month = datetime.today().strftime('%B')
            month = datetime.today().strftime('%m-%Y')
            subject = _("LR mystery for %(month)s%(subject_ext)s") % {'month': month, 'subject_ext': subject_ext}
            send_mail(subject, message, "rosary@cyberarche.pl", (email, 'rosarium.mariae.eroza@gmail.com'))
            logger.info("Send email to %s with code %s" % (email, pi.code))


def rotate_intensions(previous_intensions):
    current_intension = previous_intensions[1]
    new_intension = previous_intensions[0]
    current_person_intensions = find_person_itnensions(current_intension)
    if not current_person_intensions:
        logger.error("No person intensions for period %s" % str(current_intension))
        raise Exception("No person intensions for period ", str(current_intension))
    mysteries = [(m.number, m) for m in Mystery.objects.all()]
    mysteries_dict = dict(mysteries)
    created = []
    for pi in current_person_intensions:
        person = pi.person
        mystery_no = (pi.mystery.number % 20) + 1
        mystery = mysteries_dict[mystery_no]
        new_pi = PersonIntension(person=person, intension=new_intension, mystery=mystery)
        new_pi.save()
        created.append(new_pi)
    return created


def process_intensions():
    recent_intensions = find_recent_intensions(2)
    if not recent_intensions:
        logger.error("No current intension. Quitting")
        return
    person_intensions = find_person_itnensions(recent_intensions[0])
    if person_intensions:
        notify_not_downloaded(person_intensions, _(" - remider"))
    elif len(recent_intensions) > 1:
        created_intensions = rotate_intensions(recent_intensions)
        notify_not_downloaded(created_intensions)
    else:
        logger.error("Cannot find person intensions for period %s" % str(recent_intensions[0]))


import logging

import django

django.setup()

from django.utils import translation

language = settings.LANGUAGE_CODE
if not language:
    language = "pl-pl"

translation.activate(language)

from rosary.models import Intension, PersonIntension, Mystery

from django.core.mail import send_mail

logger = logging.getLogger(__name__)

process_intensions()
