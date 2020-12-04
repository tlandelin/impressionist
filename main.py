from time import sleep
from sys import stdout as o
import os
import csv

from impressionist.pixelizer import resize, recolor, create_stencil

CH_DELAY = 0.03
SP_DELAY = 0.1

def print_(msg, newline=True):
    for ch in msg:
        o.write(ch)
        sleep(CH_DELAY if ch.isalpha() else SP_DELAY)
        o.flush()

    if newline:
        o.write('\n')


def input_(msg):
    print_(msg)
    return input('> ').strip()

def confirm(msg):
    conf_msg = '{} (y/n)'.format(msg)
    while True:
        resp = input_(conf_msg).strip()
        if resp.lower() == 'y':
            return True
        elif resp.lower() == 'n':
            return False
        else:
            print_('invalid answer "{}". enter y or n'.format(resp))

class Done(Exception):
    pass

def choose_color(all_colors):
    choose_msg = "enter a color, or type d if done"

    while True:
        resp = input_(choose_msg).strip().lower()
        if resp == 'd':
            raise Done
        elif resp not in all_colors:
            print_('{} is not in colors collection'.format(resp))
        else:
            break
    return resp


def input_file(msg):
    while True:
        filename = input_(msg)
        if not os.path.isfile(filename):
            print_('that doesn\'t look like a valid file path. try again.')
            continue
        break
    return filename


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('colors_file',
            help=('location of the colors definition file. it is a CSV file with 2 columns'
                  '-- Name and Hex. Name is the name of the color and hex is the RGB value'
                  ' in hexadecimal')
    parser.add_argument('image_file', help='location where your picture is stored')
    parser.add_argument('-d', '--max-dimension', default=50,
        help=('the highest number of pixels you want to have converted on the length or '
              'width of the new picture')
    parser.add_argument('mode', choices=('picture', 'stencil'),
        help='whether you want to create a stencil PDF or just preview it with a picture')
    args = parser.parse_args()
    color_rgbs = {}
    with open(args.colors_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        headers = next(reader)
        for row in reader:
            color_name, rgb = row
            color_name = color_name.lower()
            r, g, b = tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))
            color_rgbs[color_name] = (r, g, b)

    image = resize(args.image_file)
    recolor(image, color_rgbs.values())

    if args.mode == 'picture':
        image.show()
    elif args.mode == 'stencil':
        create_stencil(image, color_rgbs)


