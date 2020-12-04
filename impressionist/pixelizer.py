from math import sqrt
from collections import defaultdict

from PIL import Image
from reportlab.pdfgen import canvas


MAX_SIDE = 50

def resize(image_file):
    '''lowers the resolution of the original image and finds the new colors'''
    im = Image.open(image_file, 'r')
    width, height = im.width, im.height

    # resample
    scale_factor = max(width, height) // MAX_SIDE
    new_width, new_height = width // scale_factor, height // scale_factor
    new_im = Image.new("RGB", (new_width, new_height), '#FFFFFF')
    pixels = new_im.load()

    for new_x in range(new_width):
        for new_y in range(new_height):
            r, g, b = average_pixel(im, new_x, new_y, scale_factor)
            pixels[new_x, new_y] = (r, g, b)
    return new_im


def average_pixel(img, new_x, new_y, scale_factor):
    img_x, img_y = new_x * scale_factor, new_y * scale_factor

    sum_r, sum_g, sum_b, count = 0, 0, 0, 0
    for x in range(img_x, img_x + scale_factor):
        for y in range(img_y, img_y + scale_factor):
            r, g, b = img.getpixel((x, y))
            sum_r += r
            sum_g += g
            sum_b += b
            count += 1
    return sum_r // count, sum_g // count, sum_b // count


def recolor(img, palette):
    '''re-colors the image by choosing the closest colors to the original from a palette'''
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            orig_color = img.getpixel((x, y))
            new_color = closest_color(orig_color, palette)
            pixels[x, y] = new_color

def closest_color(pixel_color, palette):
    '''finds the closest color in palette to the pixel_color'''

    def euclidean_dist(color1, color2):
        (r1, g1, b1) = color1
        (r2, g2, b2) = color2
        return sqrt((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2)

    return min(palette, key = lambda c: euclidean_dist(pixel_color, c))


def create_stencil(img, palette):
    '''writes out a pdf of the color stencil'''
    rgb_colornames = {v: k for k, v in palette.items()}

    # assign a number to each color by rgb value
    rgb_number = {color: counter for (counter, (_, color)) in enumerate(img.getcolors(maxcolors=len(palette) + 1))}

    # associate the color's number to the color names
    number_colornames = {number: rgb_colornames[rgb] for rgb, number in rgb_number.items()}

    # create the pdf stencil with a grid of numbers, with the number/color key at the bottom
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.rl_config import defaultPageSize
    from reportlab.lib.units import inch
    styles = getSampleStyleSheet()
    page_width, page_height = defaultPageSize

    def gridpage_state(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman',3)

        canvas.restoreState()

    def keypage_state(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page - 1, "Color key"))
        canvas.restoreState()

    doc = SimpleDocTemplate("grid.pdf")
    story = []

    pixels = img.load()
    number_grid = [[str(rgb_number[pixels[x, y]]) for x in range(img.width)] for y in range(img.height)]
    w_aspect = 1 if img.width >= img.height else img.width / img.height
    h_aspect = 1 if img.width <= img.height else img.height / img.width
    t = Table(number_grid, img.width * [8*inch*w_aspect / img.width], img.height * [8*inch*h_aspect / img.height], style=[('GRID',(0,0),(-1,-1),0.25,colors.black)])
    font_size = .6*8*inch*h_aspect // img.height
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t)

    story.append(PageBreak())

    style = styles["Normal"]
    for (number, colorname) in number_colornames.items():
        item = '{} - {}'.format(number, colorname)
        p = Paragraph(item, style)
        story.append(p)
        story.append(Spacer(1,0.2*inch))
    doc.build(story, onFirstPage=gridpage_state, onLaterPages=keypage_state)







