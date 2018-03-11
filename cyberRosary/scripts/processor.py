#!/usr/bin/python
from django.utils.translation import ugettext as _
from django.utils.datetime_safe import datetime

# import django
# django.setup()

from cyberRosary import settings

from rosary.models import Intension, PersonIntension, Mystery

from django.utils import translation

from mailqueue.models import MailerMessage

import logging

logger = logging.getLogger(__name__)


def find_recent_intensions(count, start_date=datetime.today()):
    # todo configure start date
    recent_intensions = Intension.objects.filter(start_date__lte=start_date).order_by('-start_date')[:count]
    return recent_intensions


def find_person_itnensions(current_intension):
    # todo: optimise query if needed - join and eager person, mystery
    person_intensions = PersonIntension.objects.filter(intension=current_intension)
    return person_intensions


def notify_not_downloaded(person_intensions, template, reminder=False):
    logger.info("Notyfying not downloaded.")
    for pi in person_intensions:
        if not template:
            lang = pi.person.language
            translation.activate(lang)
            subject_ext = _(" - reminder"))
            template = _(
                "God bless,\n Under the link \n%s\nthere is a new Live Rosary mystery.\n Pease report any problems with downloading or opening the file to rosary@cyberarche.pl email address.\nSincerely\nCyberarche Team")
        if pi.person.active and not pi.downloaded:
            url = settings.LOCATION_TEMPLATE % pi.code
            email = pi.person.email
            message = template % url
            month = datetime.today().strftime('%m-%Y')
            subject = _("LR mystery for %(month)s%(subject_ext)s") % {'month': month, 'subject_ext': subject_ext}
            send_mail(subject, message, "rosary@cyberarche.pl", email)
            logger.info("Send email to %s with code %s and body %s" % (email, pi.code, message))


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
        if person.active:
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
    current_message = recent_intensions[0].message
    if person_intensions:
        notify_not_downloaded(person_intensions, current_message, True)
    elif len(recent_intensions) > 1:
        created_intensions = rotate_intensions(recent_intensions)
        notify_not_downloaded(created_intensions, current_message)
    else:
        logger.error("Cannot find person intensions for period %s" % str(recent_intensions[0]))


def send_mail(subject, content, from_addres, to_address):
    new_message = MailerMessage()
    new_message.subject = subject
    new_message.content = content
    new_message.from_addres = from_addres
    new_message.to_address = to_address
    new_message.save()


def run():
    process_intensions()
