# -*- coding: utf-8 -*-

import logging
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
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

from cyberRosary import settings
from rosary.models import PersonIntension, Mystery

logger = logging.getLogger(__name__)


def printout(request, unique_code):
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
                            rightMargin=72, leftMargin=72,
                            topMargin=36, bottomMargin=18, title=title)

    width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

    story = []
    logo = pi.mystery.image_path.path

    # group = pi.mystery.group
    user = pi.person.name
    start_date = pi.intension.start_date
    quote = pi.mystery.quote
    meditation = pi.mystery.meditation
    intension1 = pi.intension.universal_intension
    intension2 = pi.intension.evangelisation_intension
    intension3 = pi.intension.pcm_intension
    number_group = determine_number_group(pi.mystery.group, pi.mystery.number)

    im = get_image(logo, (doc.width / 2)*.9)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterP', alignment=enums.TA_CENTER, fontName='DejaVuSerif', fontSize=10))
    styles.add(ParagraphStyle(name='JustifyP', alignment=enums.TA_JUSTIFY, fontName='DejaVuSerif', fontSize=9))
    styles.add(ParagraphStyle(name='NormalP', alignment=enums.TA_LEFT, fontName='DejaVuSerif', fontSize=9))
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

    t = Table(data, style=[('ALIGN', (1, 0), (1, 0), 'CENTER'),
                           ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                           ])

    story.append(t)

    story.append(Spacer(1, 12))

    story.append(Paragraph(u"<b>Intencja papieska ogólna</b> %s" % intension1, styles["NormalP"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(u"<b>Intencja papieska ewangelizacyjna</b> %s" % intension2, styles["NormalP"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(u"<b>Intencja PMK</b> %s" % intension3, styles["NormalP"]))
    story.append(Spacer(1, 12))

    story.append(d)

    # date
    story.append(
        Paragraph(u'<font color="red">Tajemnicę należy odmawiać od %s</font>' % str(start_date), styles["CenterP"]))
    story.append(Spacer(1, 6))


    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    now = timezone.now()

    pi.downloaded = now
    pi.save()

    return response


def index(request):
    logger.debug("index started")
    pis = PersonIntension.objects.all().prefetch_related('person', 'mystery')
    logger.debug("found: %d" % len(pis))
    context = {'pis': pis}

    return render(request, 'rosary/index.html', context)


def get_image(path, width=1 * cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def determine_number_group(group, number):
    number_in_group = number % 5
    if number_in_group < 4:
        seq = 'I' * number_in_group
    elif number_in_group < 5:
        seq = 'IV'
    else:
        seq = 'V'
    group_name = Mystery.GROUPS[group]
    return seq + ' ' + group_name
