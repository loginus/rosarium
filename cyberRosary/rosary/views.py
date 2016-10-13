from django.shortcuts import render, get_object_or_404

# Create your views here.

from io import BytesIO

from django.utils import timezone
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import enums
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageTemplate
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from rosary.models import PersonIntension

import logging

logger = logging.getLogger(__name__)

def printout(request, unique_code):

    pi = get_object_or_404(PersonIntension, code=unique_code) # type: PersonIntension

    title = pi.mystery.title



    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + title +'.pdf"'

    logger.info("Content-disposition %s"  % response['Content-Disposition'])

    buffer = BytesIO()

    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))

    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18, title=title)

    width = doc.pagesize[0]-doc.leftMargin-doc.rightMargin

    story = []
    logo = pi.mystery.image_path.path

    # group = pi.mystery.group
    user = pi.person.name
    start_date = pi.intension.start_date
    quote = pi.mystery.quote
    meditation  = pi.mystery.meditation
    intension1 = pi.intension.universal_intension
    intension2 = pi.intension.evangelisation_intension
    intension3 = pi.intension.pcm_intension

    im = Image(logo, 2 * inch, 2 * inch)


    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=enums.TA_JUSTIFY, fontName='DejaVuSerif', fontSize=10))
    styles.add(ParagraphStyle(name='NormalP', alignment=enums.TA_JUSTIFY, fontName='DejaVuSerif', fontSize=10))
    styles.add(ParagraphStyle(name='H2', alignment=enums.TA_CENTER, fontName='DejaVuSerif', fontSize=10))
    styles.add(ParagraphStyle(name='H1', alignment=enums.TA_CENTER, fontName='DejaVuSerif', fontSize=12))
    #styles.add(ParagraphStyle(name='Italic', alignment=enums.TA_LEFT, fontName='Times-Italic', fontSize=10))

    #line
    d = Drawing(doc.width, 1)
    d.add(Line(0, 0, doc.width, 0))
    story.append(d)

    #mystery group
    story.append(Paragraph("II Tajemnica Swiatla", styles["Heading2"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(title, styles["Heading1"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(quote, styles["Italic"]))
    story.append(Spacer(1, 12))

    doc.build(story)

    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width / 2 - 6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin + doc.width / 2 + 6, doc.bottomMargin, doc.width / 2 - 6, doc.height,  id='col2')

    story.append(im)
    story.append(Paragraph(meditation, styles["Justify"]))
    doc.addPageTemplates([PageTemplate(id='TwoCol', frames=[frame1, frame2]), ])

    #story.append(im)

    #story.append(Spacer(1, 12))

    #story.append(Paragraph(meditation, styles["Justify"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(intension1, styles["Justify"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(intension2, styles["Justify"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(intension3, styles["Justify"]))
    story.append(Spacer(1, 12))

    #date
    story.append(Paragraph(str(start_date), styles["NormalP"]))
    story.append(Spacer(1, 6))

    # User
    story.append(Paragraph(user, styles["NormalP"]))
    story.append(Spacer(1, 12))

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
