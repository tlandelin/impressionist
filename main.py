import csv
import os

from impressionist.pixelizer import shrink, grow, recolor, create_stencil
from PIL import Image
p = os.path

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('colors_file',
            help=('location of the colors definition file. it is a CSV file with 2 columns'
                  '-- Name and Hex. Name is the name of the color and hex is the RGB value'
                  ' in hexadecimal'))
    parser.add_argument('image_file', help='location where your picture is stored')
    parser.add_argument('-d', '--max-dimension', type=int, default=50,
        help=('the highest number of pixels you want to have converted on the length or '
              'width of the new picture'))
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


    image = Image.open(args.image_file, 'r')
    orig_max_dimension = max(image.width, image.height)
    image = shrink(image, args.max_dimension)
    recolor(image, color_rgbs.values())
    image = grow(image, orig_max_dimension // args.max_dimension)

    base_name = p.basename(args.image_file)
    base_name = p.splitext(base_name)[0]
    base_name = '{}_pixelized_{}'.format(base_name, args.max_dimension)

    if args.mode == 'picture':
        base_name = '{}.jpg'.format(base_name)
        savepath = p.join(p.dirname(args.image_file), base_name)
        image.save(savepath)
        print('wrote pixelized image to', savepath)

    elif args.mode == 'stencil':
        base_name = '{}.pdf'.format(base_name)
        savepath = p.join(p.dirname(args.image_file), base_name)
        create_stencil(image, color_rgbs, savepath)
        print('wrote stencil to', savepath)


