# -*- coding: utf-8 -*-

import logging
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import enums
from reportlab.lib import utils
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Table
from django.contrib.auth import decorators

from rosary.models import PersonIntension, Intension
from django.template.defaultfilters import date


logger = logging.getLogger(__name__)


@cache_page(3600*24*20)
def printout(request, unique_code):
    (pdf, pi) = _generate_pdf(request, unique_code)
    now = timezone.now()
    if not pi.downloaded:
        pi.downloaded = now
        pi.save()
    pi.person.last_activity = now
    pi.person.save()
    return pdf


@decorators.login_required
def index(request):
    from django.utils.datetime_safe import datetime
    logger.debug("index started")
    today = datetime.today()
    intension = Intension.objects.filter(start_date__lte=today).order_by('-start_date')[0]
    if not intension:
        pis = []
    else:
        pis = PersonIntension.objects.filter(intension=intension, person__active=True).order_by('mystery__number').prefetch_related('person',
                                                                                                               'mystery')
    logger.debug("found: %d" % len(pis))
    not_downloaded = sum(not pi.downloaded for pi in pis)
    last_downloaded = max(pi.downloaded for pi in pis if pi.downloaded)
    context = {'pis': pis, 'not_downloaded' : not_downloaded, 'last_downloaded' : last_downloaded}


    return render(request, 'rosary/index.html', context)


@decorators.login_required
def check_printout(request, unique_code):
    (pdf, pi) = _generate_pdf(request, unique_code)
    return pdf


def _generate_pdf(request, unique_code):
    logger.info("Download request from client %s (%s), agent '%s', referer '%s' " % (request.META.get('REMOTE_ADDR'),
                                                                                     request.META.get('REMOTE_HOST'),
                                                                                     request.META.get('HTTP_USER_AGENT'),
                                                                                     request.META.get('HTTP_REFERER'),
                                                                                     )
                )
    pi = get_object_or_404(PersonIntension, code=unique_code)  # type: PersonIntension
    title = pi.mystery.title
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + title + '.pdf"'
    logger.info("Content-disposition %s" % response['Content-Disposition'])
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSerifBd', 'DejaVuSerif-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSerifIt', 'DejaVuSerif-Italic.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSerifBI', 'DejaVuSerif-BoldItalic.ttf'))
    registerFontFamily('DejaVuSerif', normal='DejaVuSerif', bold='DejaVuSerifBd', italic='DejaVuSerifIt',
                       boldItalic='DejaVuSerifBI')
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=54, leftMargin=54,
                            topMargin=36, bottomMargin=18, title=title)
    width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin
    story = []
    logo = pi.mystery.image_path.path
    # group = pi.mystery.group
    user = pi.person.name
    start_date = pi.intension.start_date
    end_date = pi.intension.end_date
    quote = _prepare_text(pi.mystery.quote)
    meditation = _prepare_text(pi.mystery.meditation)
    intension1 = pi.intension.papal_intension
    intension3 = pi.intension.pcm_intension
    logger.info("Generating mystery '%s' for user: %s" % (title, user))
    number_group = pi.mystery.number_group()
    normal_font_size = _determine_font_size(meditation, quote)
    im = _get_image(logo, (doc.width / 2) * .9)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterP', alignment=enums.TA_CENTER, fontName='DejaVuSerif', fontSize=10))
    styles.add(
        ParagraphStyle(name='NormalP', alignment=enums.TA_LEFT, fontName='DejaVuSerif', fontSize=normal_font_size))
    styles.add(ParagraphStyle(name='H2', alignment=enums.TA_CENTER, fontName='DejaVuSerifBd', fontSize=10))
    styles.add(ParagraphStyle(name='H1', alignment=enums.TA_CENTER, fontName='DejaVuSerifBd', fontSize=12))
    # User
    story.append(Paragraph(user, styles["NormalP"]))
    story.append(Spacer(1, 12))
    # line
    d = Drawing(doc.width, 1)
    d.add(Line(0, 0, doc.width, 0))
    story.append(d)
    # mystery group
    story.append(Spacer(1, 6))
    story.append(Paragraph(number_group, styles["H2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(title, styles["H1"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(u"<i>%s</i>" % quote, styles["NormalP"]))
    story.append(Spacer(1, 12))
    meditationParagraph = Paragraph(meditation, styles["NormalP"])
    data = [[meditationParagraph, im]]
    t = Table(data, style=[
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
    ])
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph(_("<b>%s</b>") % date(start_date, 'F Y'), styles["NormalP"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(_("<b>Papal Intention:</b> %s") % intension1, styles["NormalP"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(_("<b>Intension of Polish Catholic Mission:</b> %s") % intension3, styles["NormalP"]))
    story.append(Spacer(1, 12))
    story.append(d)
    story.append(Spacer(1, 6))
    # date
    story.append(
        Paragraph(
            '<font color="red">'
            + _('Mystery ought to be prayed from %(date_from)s to %(date_to)s')
            % {'date_from': str(start_date), 'date_to': str(end_date)}
            + '</font>', styles["CenterP"]))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return (response, pi)


def _get_image(path, width=1 * cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def _determine_font_size(meditation, quote):
    normal_font_size = 9
    if len(quote) + 2 * len(meditation) > 3500:
        normal_font_size = 8
    return normal_font_size


def _prepare_text(text):
    if text:
        return text.strip().replace('\n', '<br/>')
    return text
