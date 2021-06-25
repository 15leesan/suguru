from itertools import count
from typing import NamedTuple
from PIL import Image, ImageDraw, ImageFont
import colorsys
from functools import cache
from random import shuffle, seed

blocks = [
    "112223",
    "411223",
    "445533",
    "446553",
    "666657",
    "887777",
]
width = len(blocks[0])
height = len(blocks)

starters = { }
starters[(1, 1)] = 1
starters[(0, 3)] = 2
starters[(0, 5)] = 1
starters[(5, 0)] = 1
starters[(5, 2)] = 3
starters[(5, 5)] = 2
starters[(2, 5)] = 4
starters[(2, 4)] = 3

@cache
def get_coords_in_block(index):
    l = []
    for y in range(height):
        for x in range(width):
            if blocks[y][x] == str(index):
                l.append((x, y))
    return l

@cache
def get_block_from_coords(x, y):
    return int(blocks[y][x])

num_blocks = len({ blocks[y][x] for y in range(height) for x in range(width) })
seed(hash(frozenset(starters.items())))
colors = [tuple(int(k * 255) for k in colorsys.hsv_to_rgb(i / num_blocks, 0.5, 0.8)) for i in range(num_blocks)]
shuffle(colors)

img = Image.new("RGB", size=(height, width), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
for y in range(height):
    for x in range(width):
        img.putpixel((x, y), colors[int(blocks[y][x]) - 1])

line_scale = 24
second_scale = 2
scale = line_scale * second_scale
img = img.resize((width * line_scale, height * line_scale))
draw = ImageDraw.Draw(img)

line_pos = lambda x, y:(x * line_scale - 1, y * line_scale - 1)
# draw.line([(x * line_scale, y * line_scale) for x, y in get_block_edge_points(5)], width=1, fill=(0, 0, 0))
line_args = { "fill":(100, 100, 100), "width":2 }
for y in range(height):
    for x in range(width):
        current = blocks[y][x]
        # Up
        if y == 0:
            draw.line([line_pos(x, y), line_pos(x + 1, y)], **line_args)
        elif blocks[y - 1][x] != current:
            draw.line([line_pos(x, y), line_pos(x + 1, y)], **line_args)
        
        # Down
        if y == height - 1:
            draw.line([line_pos(x, y + 1), line_pos(x + 1, y + 1)], **line_args)
        
        # Left
        if x == 0:
            draw.line([line_pos(x, y), line_pos(x, y + 1)], **line_args)
        elif blocks[y][x - 1] != current:
            draw.line([line_pos(x, y), line_pos(x, y + 1)], **line_args)
        
        # Right
        if x == width - 1:
            draw.line([line_pos(x + 1, y), line_pos(x + 1, y + 1)], **line_args)

img = img.resize((width * scale, height * scale))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", scale)

cell_pos = lambda x, y:((x + 0.5) * scale, (y + 0.5) * scale)

DefaultCell = { "possible":{ 1, 2, 3, 4, 5, 6, 7, 8, 9 }, "actual":None, "found":False, "starter":False }
grid = []
for y in range(height):
    grid.append([])
    for x in range(width):
        grid[y].append(DefaultCell.copy())
        grid[y][x]["possible"] = DefaultCell["possible"].copy()

for pos in starters.keys():
    x, y = pos
    val = starters[pos]
    grid[y][x]["possible"].clear()
    grid[y][x]["possible"].add(val)
    grid[y][x]["found"] = True
    grid[y][x]["actual"] = val
    grid[y][x]["starter"] = True


def remove_at(x, y, val):
    if x < 0 or x >= width or y < 0 or y >= height: return
    if val in grid[y][x]["possible"]:
        grid[y][x]["possible"].remove(val)


def update_at(x, y):
    if x < 0 or x >= width or y < 0 or y >= height: return
    if grid[y][x]["found"]: return
    if len(grid[y][x]["possible"]) == 1:
        grid[y][x]["found"] = True
        grid[y][x]["actual"] = grid[y][x]["possible"].copy().pop()


for i in range(1, num_blocks + 1):
    cells = get_coords_in_block(i)
    size = len(cells)
    for cell in cells:
        x, y = cell
        grid[y][x]["possible"] = { k for k in grid[y][x]["possible"] if k <= size }

should_continue = True
for i in count():
    should_continue = False
    for y in range(height):
        for x in range(width):
            if not grid[y][x]["found"]:
                should_continue = True
                continue
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == dy == 0: continue
                    remove_at(x + dx, y + dy, grid[y][x]["actual"])
                    update_at(x + dx, y + dy)
            for cell in get_coords_in_block(get_block_from_coords(x, y)):
                if cell != (x, y):
                    remove_at(cell[0], cell[1], grid[y][x]["actual"])
                    update_at(cell[0], cell[1])
    if not should_continue:
        print(f"Took {i} iterations")
        break

for y in range(height):
    for x in range(width):
        current = grid[y][x]
        col = (100, 100, 100) if current["starter"] else (0, 0, 0)
        actual = current["actual"] if current["found"] else ""
        
        draw.text(cell_pos(x, y), str(actual), font=font, anchor="mm", fill=col)

img.save("sugu.png")