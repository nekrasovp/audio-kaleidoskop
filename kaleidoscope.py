#!/usr/bin/env python
"""
Kaleidoscope
"""

import numpy
from PIL import Image, ImageDraw, ImageOps


def is_odd(num):
    return num % 2 != 0


# This bit of maths could be simplified for our case, but it gets the job done
# From http://stackoverflow.com/a/6959111/724176
def transformblit(src_tri, dst_tri, src_img, dst_img):
    ((x11, x12), (x21, x22), (x31, x32)) = src_tri
    ((y11, y12), (y21, y22), (y31, y32)) = dst_tri

    M = numpy.array(
        [
            [y11, y12, 1, 0, 0, 0],
            [y21, y22, 1, 0, 0, 0],
            [y31, y32, 1, 0, 0, 0],
            [0, 0, 0, y11, y12, 1],
            [0, 0, 0, y21, y22, 1],
            [0, 0, 0, y31, y32, 1],
        ]
    )

    y = numpy.array([x11, x21, x31, x12, x22, x32])

    A = numpy.linalg.solve(M, y)

    src_copy = src_img.copy()
    srcdraw = ImageDraw.Draw(src_copy)
    srcdraw.polygon(src_tri)
    #     src_copy.show()
    transformed = src_img.transform(dst_img.size, Image.AFFINE, A)

    mask = Image.new("1", dst_img.size)
    maskdraw = ImageDraw.Draw(mask)
    maskdraw.polygon(dst_tri, fill=255)

    dstdraw = ImageDraw.Draw(dst_img)
    dstdraw.polygon(dst_tri, fill="white")
    #     dst_img.show()
    dst_img.paste(transformed, mask=mask)
    # dst_img.show()


def kaleidoscope(triangle_width, infile):
    triangle_height = int(triangle_width * numpy.sqrt(3) / 2)

    img = Image.open(infile).convert("RGBA")
    width, height = img.size
    centre_point = (width / 2, height / 2)
    top_of_triangle = (height / 2) - (triangle_height / 2)
    bottom_of_triangle = top_of_triangle + triangle_height
    left_of_triangle = (width / 2) - (triangle_width / 2)
    right_of_triangle = left_of_triangle + triangle_width
    # Triangle zero
    a = (centre_point[0], top_of_triangle)
    b = (right_of_triangle, bottom_of_triangle)
    c = (left_of_triangle, bottom_of_triangle)
    # x is leftmost point of next triangle
    x = centre_point[0]
    i = 0
    tri1 = [a, b, c]
    new_a = a
    new_b = b
    new_c = c
    # (Every third image is a vertical flip, so an optimisation would be to
    # calculate just the three rotated triangles and paste flips as needed.
    # These three flips could also be cached.)

    # Fill to the right
    while x < width:
        i += 1
        # print(i, x, width)

        if is_odd(i):
            new_y = top_of_triangle
        else:
            new_y = bottom_of_triangle

        if i % 3 == 1:
            new_c = (new_c[0] + (1.5 * triangle_width), new_y)
        elif i % 3 == 2:
            new_a = (new_a[0] + (1.5 * triangle_width), new_y)
        elif i % 3 == 0:
            new_b = (new_b[0] + (1.5 * triangle_width), new_y)
        tri2 = [new_a, new_b, new_c]
        transformblit(tri1, tri2, img, img)

        x += triangle_width / 2

    # x is rightmost point of next triangle
    x = centre_point[0]
    i = 0
    new_a = a
    new_b = b
    new_c = c

    # Fill to the left
    while x > 0:
        i += 1
        # print(i, x, width)

        if is_odd(i):
            new_y = top_of_triangle
        else:
            new_y = bottom_of_triangle

        if i % 3 == 1:
            new_b = (new_b[0] - (1.5 * triangle_width), new_y)
        elif i % 3 == 2:
            new_a = (new_a[0] - (1.5 * triangle_width), new_y)
        elif i % 3 == 0:
            new_c = (new_c[0] - (1.5 * triangle_width), new_y)
        tri2 = [new_a, new_b, new_c]
        transformblit(tri1, tri2, img, img)

        x -= triangle_width / 2

    # Flip strip
    strip = img.crop((0, top_of_triangle, width, bottom_of_triangle))
    flip = ImageOps.flip(strip)

    # Fill down
    y = bottom_of_triangle
    i = 0
    while y < height:
        # print(y, height)
        i += 1
        if is_odd(i):
            img.paste(flip, (0, int(y)))
        else:
            img.paste(strip, (0, int(y)))
        y += triangle_height

    # Fill up
    y = top_of_triangle
    i = 0
    while y > 0:
        # print(y, 0)
        i += 1
        if is_odd(i):
            img.paste(flip, (0, int(y - triangle_height)))
        else:
            img.paste(strip, (0, int(y - triangle_height)))
        y -= triangle_height

    return img
