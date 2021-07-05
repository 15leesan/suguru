from typing import List, Tuple
from PIL import Image, ImageDraw
from random import seed, shuffle
import colorsys

grid_size = (6, 6)

ALL_LINES = True

_threshold = 95

thick_lines = []


def get_thick_lines():
    return thick_lines


def set_threshold(thresh):
    global _threshold
    _threshold = thresh


def set_grid_size(x, y):
    global grid_size
    grid_size = (x, y)


def get_pixel_line_horizontal(im: Image.Image, x1, y, x2):
    points = []
    if x1 > x2:
        x1, x2 = x2, x1
    for x in range(x1, x2):
        points.append(im.getpixel((x, y)))
    return points


def get_pixel_line_vertical(im: Image.Image, x, y1, y2):
    points = []
    if y1 > y2:
        y1, y2 = y2, y1
    for y in range(y1, y2):
        points.append(im.getpixel((x, y)))
    return points


def get_mid_color(l: List[Tuple[int, int, int]]):
    size = len(l)
    assert size > 10
    center = size // 2
    width = round(size / 10)
    part = l[center - width: center + width]
    min_r = min([p[0] for p in part])
    min_g = min([p[1] for p in part])
    min_b = min([p[2] for p in part])
    
    if min_r <= _threshold and min_g <= _threshold and min_b <= _threshold:
        return (min_r, min_g, min_b)
    return (0, 100, 255)


def get_block_shapes(path):
    im: Image.Image = Image.open(path)
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(im)
    width, height = im.size
    cell_width, cell_height = width / grid_size[0], height / grid_size[1]
    
    get_pos = lambda x, y: (round((x + 0.5) * cell_width), round((y + 0.5) * cell_height))
    
    left_edges = []
    right_edges = []
    up_edges = []
    down_edges = []
    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            pos = get_pos(x, y)
            if x != 0:
                col = get_mid_color(get_pixel_line_horizontal(im, pos[0], pos[1], get_pos(x - 1, y)[0]))
                if ALL_LINES:
                    draw.line(
                            [pos, get_pos(x - 1, y)],
                            fill=col,
                            width=3)
                if col == (0, 100, 255):
                    left_edges.append((x, y))
                    right_edges.append((x - 1, y))
                    draw.line(
                            [pos, get_pos(x - 1, y)],
                            fill=col,
                            width=3)
                else:
                    thick_lines.append((x, y, x, y + 1))
            if y != 0:
                col = get_mid_color(get_pixel_line_vertical(im, pos[0], pos[1], get_pos(x, y - 1)[1]))
                if ALL_LINES:
                    draw.line(
                            [pos, get_pos(x, y - 1)],
                            fill=col,
                            width=3)
                if col == (0, 100, 255):
                    up_edges.append((x, y))
                    down_edges.append((x, y - 1))
                    draw.line(
                            [pos, get_pos(x, y - 1)],
                            fill=col,
                            width=3)
                else:
                    thick_lines.append((x, y, x + 1, y))
    
    marked_cells = set()
    blocks = []
    cell_to_block = {}
    for i in range(grid_size[0] * grid_size[1]):
        # for i in range(1):
        start_pos = None
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                if (x, y) not in marked_cells:
                    start_pos = (x, y)
                    break
            if start_pos is not None:
                break
        index_cells = set()
        index_cells.add(start_pos)
        for j in range(10):  # Depth to search
            for cell in index_cells.copy():
                cell_x, cell_y = cell
                if cell in left_edges: index_cells.add((cell_x - 1, cell_y))
                if cell in right_edges: index_cells.add((cell_x + 1, cell_y))
                if cell in up_edges: index_cells.add((cell_x, cell_y - 1))
                if cell in down_edges: index_cells.add((cell_x, cell_y + 1))
        for cell in index_cells:
            cell_to_block[cell] = i
        blocks.append(index_cells)
        marked_cells.update(index_cells)
        if len(marked_cells) == grid_size[0] * grid_size[1]:
            break

    num_blocks = len(blocks)
    seed(hash(frozenset([hash(frozenset(k)) for k in blocks])))
    colors = [tuple(int(k * 255) for k in colorsys.hsv_to_rgb(i / num_blocks, 0.5, 0.8)) for i in range(num_blocks)]
    shuffle(colors)
    
    text_map = []
    for y in range(grid_size[1]):
        text_map.append([])
        for x in range(grid_size[0]):
            pos = get_pos(x, y)
            block_no = cell_to_block[(x, y)]
            color = colors[block_no]
            draw.ellipse([pos[0] - 5, pos[1] - 5, pos[0] + 5, pos[1] + 5], fill=color)
            text_map[y].append(str(block_no + 1))
    
    text = "\n".join([".".join(line) for line in text_map])
    im.save("lines.png")
    
    return text


if __name__ == '__main__':
    print(get_block_shapes())