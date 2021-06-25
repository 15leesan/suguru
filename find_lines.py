from typing import List, Tuple
from PIL import Image, ImageDraw

grid_size = (6, 6)

def get_pixel_line_horizontal(im : Image.Image, x1, y, x2):
    points = []
    if x1 > x2:
        x1, x2 = x2, x1
    for x in range(x1, x2):
        points.append(im.getpixel((x, y)))
    return points


def get_pixel_line_vertical(im : Image.Image, x, y1, y2):
    points = []
    if y1 > y2:
        y1, y2 = y2, y1
    for y in range(y1, y2):
        points.append(im.getpixel((x, y)))
    return points

def get_mid_color(l : List[Tuple[int, int, int]]):
    size = len(l)
    assert size > 10
    center = size // 2
    part = l[center - 5: center + 5]
    min_r = min([p[0] for p in part])
    min_g = min([p[1] for p in part])
    min_b = min([p[2] for p in part])
    return (min_r, min_g, min_b)

if __name__ == "__main__":
    im : Image.Image = Image.open("target.png")
    draw : ImageDraw.ImageDraw = ImageDraw.Draw(im)
    width, height = im.size
    cell_width, cell_height = width / grid_size[0], height / grid_size[1]

    get_pos = lambda x, y : (round((x + 0.5) * cell_width), round((y + 0.5) * cell_height))
    pos = get_pos(0, 1)
    pos2 = get_pos(1, 1)
    draw.ellipse([pos[0] - 5, pos[1] - 5, pos[0] + 5, pos[1] + 5], fill=(255, 0, 0))
    draw.ellipse([pos2[0] - 5, pos2[1] - 5, pos2[0] + 5, pos2[1] + 5], fill=(255, 0, 0))

    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            pos = get_pos(x, y)
            if x != 0:
                draw.line(
                    [pos, get_pos(x - 1, y)], 
                    fill=get_mid_color(
                        get_pixel_line_horizontal(im, pos[0], pos[1], get_pos(x - 1, y)[0])
                        ),
                    width=3)
            if y != 0:
                draw.line(
                    [pos, get_pos(x, y - 1)], 
                    fill=get_mid_color(
                        get_pixel_line_vertical(im, pos[0], pos[1], get_pos(x, y - 1)[1])
                        ),
                    width=3)
            draw.ellipse([pos[0] - 5, pos[1] - 5, pos[0] + 5, pos[1] + 5], fill=(255, 0, 0))


    im.save("lines.png")