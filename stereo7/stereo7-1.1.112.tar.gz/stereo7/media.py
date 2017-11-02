from PIL import Image


def launch_images(infile, sizes=None, filename_format='{}x{}.png'):
    if sizes is None:
        sizes = [
            (640, 960),
            (640, 1136),
            (1024, 768),
            (2048, 1536),
            (2208, 1242),
        ]

    for size in sizes:
        outfile = filename_format.format(size[0], size[1])
        im = Image.open(infile)
        if size[0] < size[1]:
            s = max(im.width, im.height)
            im = im.resize((s, s), 1)
            im = im.rotate(-90)
            im = im.resize((size[0], size[1]), 1)
            im.save(outfile, "PNG")

        rx = 1.0 * size[0] / im.width
        ry = 1.0 * size[1] / im.height

        if rx != ry:
            r = max(rx, ry)
            rsize = (int(im.width * r), int(im.height * r))
            im = im.resize(rsize, 1)
            l = (rsize[0] - size[0]) / 2
            r = im.width - l
            t = (rsize[1] - size[1]) / 2
            b = im.height - t
            im = im.crop((l, t, r, b))
        else:
            im = im.resize(size, 1)
        im = im.resize(size, 1)
        im.save(outfile, "PNG")


def icons(infile, sizes=None, filename_format='Icon-{}.png'):
    if sizes is None:
        sizes = [20, 29, 32, 40, 48, 58, 60, 72, 76, 80, 87, 96, 120, 152, 167, 180, 512, 1024]
    for size in sizes:
        outfile = filename_format.format(size)
        im = Image.open(infile)
        im.thumbnail((size, size), Image.ANTIALIAS)
        im.save(outfile, "PNG")


if __name__ == '__main__':
    launch_images('1920x1080.png')
