from itertools import count
from typing import NamedTuple
from PIL import Image, ImageDraw, ImageFont
import colorsys
from functools import cache
from random import shuffle, seed
from pprint import pprint
from typing import Tuple, List, Set, Dict

Coordinate = Tuple[int, int]


def solve(blocks, starters):
    width = len(blocks[0])
    height = len(blocks)
    
    def get_coords_in_block(index):
        l = []
        for y in range(height):
            for x in range(width):
                if blocks[y][x] == str(index):
                    l.append((x, y))
        return l
    
    def get_block_index_from_coords(x, y):
        return int(blocks[y][x])

    def get_other_coords_in_block(x, y):
        block = get_coords_in_block(get_block_index_from_coords(x, y))
        block = [coord for coord in block if coord != (x, y)]
        return block
    
    num_blocks = len({blocks[y][x] for y in range(height) for x in range(width)})
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
    
    line_pos = lambda x, y: (x * line_scale - 1, y * line_scale - 1)
    # draw.line([(x * line_scale, y * line_scale) for x, y in get_block_edge_points(5)], width=1, fill=(0, 0, 0))
    line_args = {"fill": (100, 100, 100), "width": 2}
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
    
    cell_pos = lambda x, y: ((x + 0.5) * scale, (y + 0.5) * scale)
    
    DefaultCell = {"possible": {1, 2, 3, 4, 5, 6, 7, 8, 9}, "actual": None, "found": False, "starter": False}
    grid = []
    for y in range(height):
        grid.append([])
        for x in range(width):
            grid[y].append(DefaultCell.copy())
            grid[y][x]["possible"] = DefaultCell["possible"].copy()
            grid[y][x]["position"] = (x, y)
    
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
        if grid[y][x]["found"]:
            for cell in get_coords_in_block(get_block_index_from_coords(x, y)):
                if cell != (x, y):
                    if not grid[cell[1]][cell[0]]["found"]:
                        if grid[y][x]["actual"] in grid[cell[1]][cell[0]]["possible"]:
                            grid[cell[1]][cell[0]]["possible"].remove(grid[y][x]["actual"])
            grid[y][x]["possible"] = set([grid[y][x]["actual"]])
            return
        if len(grid[y][x]["possible"]) == 1:
            grid[y][x]["found"] = True
            grid[y][x]["actual"] = grid[y][x]["possible"].copy().pop()
    
    def update_all():
        for y in range(height):
            for x in range(width):
                update_at(x, y)
    
    def find_other_neighbors(x, y) -> Set[Coordinate]:
        coords = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0: continue
                coords.add((x + dx, y + dy))
        return coords

    def find_all_neighbors(x, y) -> Set[Coordinate]:
        coords = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                coords.add((x + dx, y + dy))
        return coords
    
    def find_common_neighbors(positions: Set[Coordinate]):
        commons: Set[Coordinate] = None
        for coord in positions:
            current_coords: Set[Coordinate] = find_all_neighbors(coord[0], coord[1])
            if commons is None:
                commons = current_coords
            else:
                commons.intersection_update(current_coords)
        if commons is None:
            return set()
        return commons
    
    for i in range(1, num_blocks + 1):
        cells = get_coords_in_block(i)
        size = len(cells)
        for cell in cells:
            x, y = cell
            grid[y][x]["possible"] = {k for k in grid[y][x]["possible"] if k <= size}
    
    for i in count():
        should_continue = False
        update_all()
        for block_index in range(1, num_blocks + 1):
            coord_list = get_coords_in_block(block_index)
            block_size = len(coord_list)
            found_actuals = {i: None for i in range(1, block_size + 1)}
            for pos in coord_list:
                cell = grid[pos[1]][pos[0]]
                for possibility in cell["possible"]:
                    if found_actuals[possibility] is None:
                        found_actuals[possibility] = pos
                    elif type(found_actuals[possibility]) == tuple:
                        found_actuals[possibility] = True
            for number in found_actuals:
                value = found_actuals[number]
                if type(value) == tuple:
                    x, y = value
                    grid[y][x]["found"] = True
                    grid[y][x]["actual"] = number
            
            current_coords_by_possibilities: Dict[int, Set[Coordinate]] = {}
            for index in range(1, 10):
                current_coords_by_possibilities[index] = set()
            for pos in coord_list:
                cell = grid[pos[1]][pos[0]]
                if cell["found"]: continue
                for possibility in cell["possible"]:
                    current_coords_by_possibilities[possibility].add(pos)
            # print(current_coords_by_possibilities)
            for index in range(1, 10):
                if len(current_coords_by_possibilities[index]) <= 1: continue
                neighbors = find_common_neighbors(current_coords_by_possibilities[index])
                external_common = [coord for coord in neighbors if coord not in coord_list]
                for external_pos in external_common:
                    remove_at(external_pos[0], external_pos[1], index)
            #     print(external_common)
            #     print(index, neighbors, current_coords_by_possibilities[index])
            # print(current_coords_by_possibilities)
        update_all()
        for y in range(height):
            for x in range(width):
                if not grid[y][x]["found"]:
                    should_continue = True
                    continue
                for cell in find_other_neighbors(x, y):
                    remove_at(cell[0], cell[1], grid[y][x]["actual"])
                    update_at(cell[0], cell[1])
                for cell in get_coords_in_block(get_block_index_from_coords(x, y)):
                    if cell != (x, y):
                        remove_at(cell[0], cell[1], grid[y][x]["actual"])
                        update_at(cell[0], cell[1])
        
        # # pprint(grid)
        # for y in range(height):
        #     for x in range(width):
        #         current = grid[y][x]
        #         col = (100, 100, 100) if current["starter"] else (0, 0, 0)
        #         actual = current["actual"] if current["found"] else ""
        #
        #         draw.text(cell_pos(x, y), str(actual), font=font, anchor="mm", fill=col)
        # img.save("sugu.png")
        # pprint([grid[p[1]][p[0]] for p in get_coords_in_block(4)])
        # input(">")
        
        
        if i > width * height:
            should_continue = False
            print("Did not finish!")

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


if __name__ == '__main__':
    test_blocks = [
        "111122",
        "334122",
        "344452",
        "364555",
        "366758",
        "668888"
    ]

    test_starters = {}
    test_starters[(0, 1)] = 2
    test_starters[(1, 4)] = 4
    test_starters[(1, 5)] = 1
    test_starters[(2, 0)] = 5
    test_starters[(3, 5)] = 3
    test_starters[(4, 0)] = 1
    test_starters[(5, 4)] = 5
    
    solve(test_blocks, test_starters)
