import csv
import os
import sys
import string

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
    parser.add_argument('-o', '--output-dir', help="output directory. defaults to directory of image file")
    args = parser.parse_args()

    img_extension = p.splitext(args.image_file)[-1]
    if img_extension.lower() not in ('.jpg', '.jpeg'):
        print('image file {} does not end with .jpg or .jpeg'.format(args.image_file))
        sys.exit(1)

    color_rgbs = {}
    try:
        with open(args.colors_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = next(reader)
            for line, row in enumerate(reader, start=2):
                if len(row) != 2:
                    raise ValueError('wrong number of items on line {}'.format(line))
                color_name, rgb = row
                if len(rgb) != 6 or any(c not in string.hexdigits for c in rgb.lower()):
                    raise ValueError('RGB color ({}) is not formatted properly for {}, line {}. Expecting 6 hex characters'.format(rgb, color_name, line))
                color_name = color_name.lower()
                r, g, b = tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))
                color_rgbs[color_name] = (r, g, b)
    except ValueError as e:
        print("Error reading colors file: ", e)
        sys.exit(1)
    except Exception as e:
        print("Error with CSV format: ", e)
        sys.exit(1)


    image = Image.open(args.image_file, 'r')
    orig_max_dimension = max(image.width, image.height)
    if args.max_dimension > orig_max_dimension:
        print("max dimension can't be bigger than the maximum dimension of the original image ({})".format(orig_max_dimension))
        sys.exit(1)

    image = shrink(image, args.max_dimension)
    recolor(image, color_rgbs.values())
    image = grow(image, orig_max_dimension // args.max_dimension)

    base_name = p.basename(args.image_file)
    base_name = p.splitext(base_name)[0]
    base_name = '{}_pixelized_{}'.format(base_name, args.max_dimension)

    dir_name = args.output_dir or p.dirname(args.image_file)

    if args.mode == 'picture':
        base_name = '{}.jpg'.format(base_name)
        savepath = p.join(dir_name, base_name)
        image.save(savepath)
        print('wrote pixelized image to', savepath)

    elif args.mode == 'stencil':
        base_name = '{}.pdf'.format(base_name)
        savepath = p.join(dir_name, base_name)
        create_stencil(image, color_rgbs, savepath)
        print('wrote stencil to', savepath)


