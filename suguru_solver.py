from itertools import count
from typing import NamedTuple
from PIL import Image, ImageDraw, ImageFont
import colorsys
from functools import cache
from random import shuffle, seed
from pprint import pprint
from typing import Tuple, List, Set, Dict

Coordinate = Tuple[int, int]
GUESSING_ENABLED = False


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
    original_image = img.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", scale)
    small_font = ImageFont.truetype("arial.ttf", scale // 10)
    
    cell_pos = lambda x, y: ((x + 0.5) * scale, (y + 0.5) * scale)
    
    DefaultCell = {"possible": {1, 2, 3, 4, 5, 6, 7, 8, 9}, "actual": None, "found": False, "starter": False, "guess": False, "original_possible": None}
    grid: List[List[Dict]] = []
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
            grid[y][x]["possible"] = {grid[y][x]["actual"]}
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
    
    def copy_grid():
        copy = []
        for y in range(len(grid)):
            old_row = grid[y]
            copy_row = []
            for x in range(len(old_row)):
                old_cell = grid[y][x]
                new_cell = {k: old_cell[k].copy() if hasattr(old_cell[k], "copy") else old_cell[k] for k in old_cell}
                copy_row.append(new_cell)
            copy.append(copy_row)
        return copy
    
    def grids_same(old):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if old[y][x] != grid[y][x]:
                    return False
        return True
    
    def check_validity() -> bool:
        for y in range(height):
            for x in range(width):
                if len(grid[y][x]["possible"]) == 0:
                    return False
                if not grid[y][x]["found"]:
                    continue
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == dy == 0: continue
                        if not (0 <= x + dx < width and 0 <= y + dy < height): continue

                        if grid[y][x]["actual"] == grid[y + dy][x + dx]["actual"]:
                            print(f"Failure! Two digits next to each other at {x, y} and {x + dx, y + dy}: {grid[y][x]['actual']}")
                            return False
                for other_cell in get_other_coords_in_block(x, y):
                    if grid[y][x]["actual"] == grid[other_cell[1]][other_cell[0]]["actual"]:
                        print("Failure! Two digits in the same block")
                        return False
        return True
    
    for i in range(1, num_blocks + 1):
        cells = get_coords_in_block(i)
        size = len(cells)
        for cell in cells:
            x, y = cell
            grid[y][x]["possible"] = {k for k in grid[y][x]["possible"] if k <= size}

    old_grid = copy_grid()
    if GUESSING_ENABLED:
        guesses_stack = []
    for i in count():
        should_continue = False
        update_all()
        # https://pzl.org.uk/suguru.html#Algorithms
        for block_index in range(1, num_blocks + 1):
            coord_list = get_coords_in_block(block_index)
            block_size = len(coord_list)
            
            # Hidden single
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
                # print(index, external_common)
            #     print(index, neighbors, current_coords_by_possibilities[index])
            # print(current_coords_by_possibilities)
        update_all()
        for y in range(height):
            for x in range(width):
                number_possible = len(grid[y][x]["possible"])
                if number_possible == 2:
                    for other_cell in get_coords_in_block(get_block_index_from_coords(x, y)):
                        # Naked pairs
                        if other_cell == (x, y): continue
                        if grid[y][x]["possible"] == grid[other_cell[1]][other_cell[0]]["possible"]:
                            for removal_coord in get_coords_in_block(get_block_index_from_coords(x, y)):
                                if removal_coord == (x, y) or removal_coord == other_cell: continue
                                removal_cell = grid[removal_coord[1]][removal_coord[0]]
                                [removal_cell["possible"].remove(possibility) for possibility in grid[y][x]["possible"] if possibility in removal_cell["possible"]]
                should_continue = True
                
                for cell in find_other_neighbors(x, y):
                    # Forbidden neighbor
                    remove_at(cell[0], cell[1], grid[y][x]["actual"])
                    update_at(cell[0], cell[1])
                for cell in get_coords_in_block(get_block_index_from_coords(x, y)):
                    # Exclusion rule
                    if cell != (x, y):
                        remove_at(cell[0], cell[1], grid[y][x]["actual"])
                        update_at(cell[0], cell[1])
               
        if i > width * height:
            should_continue = False
            print("Did not finish!")

        if not should_continue:
            print(f"Took {i} iterations")
            break
        
        if GUESSING_ENABLED:
            if grids_same(old_grid):
                # Find a cell with only two possibilities
                guess_cell = None
                for y in range(height):
                    for x in range(width):
                        candidate = grid[y][x]
                        if len(candidate["possible"]) == 2:
                            guess_cell = (x, y)
                            break
                    if guess_cell is not None:
                        break
                print(f"Failure, attempting guessing at {guess_cell}")
                x, y = guess_cell
                guess_state = copy_grid()
                grid[y][x]["guess"] = True
                grid[y][x]["original_possible"] = grid[y][x]["possible"].copy()
                grid[y][x]["actual"] = grid[y][x]["possible"].pop()
                grid[y][x]["found"] = grid[y][x]["actual"]
                grid[y][x]["possible"] = set([grid[y][x]["actual"]])
                guesses_stack.append({"state": guess_state, "guess_cell": guess_cell, "guessed": grid[y][x]["actual"]})
        
        if GUESSING_ENABLED:
            if len(guesses_stack) > 0:
                if not check_validity():
                    # Guess was incorrect
                    print("Incorrect guess, restoring...")
                    guess_cell = guesses_stack[-1]["guess_cell"]
                    guess_state = guesses_stack[-1]["state"]
                    chosen = guesses_stack[-1]["guessed"]
                    print(guess_cell)
                    incorrect_grid = grid
                    grid = guess_state
                    grid[guess_cell[1]][guess_cell[0]]["possible"].remove(chosen)
                    print(grid[guess_cell[1]][guess_cell[0]])
                    del guesses_stack[-1]
                    for y in range(height):
                        for x in range(width):
                            current = grid[y][x]
                            col = (100, 100, 100) if current["starter"] else (0, 0, 0)
                            actual = current["actual"] if current["found"] else ""
            
                            for num in range(1, 10):
                                small_pos = ((x + (num / 12)) * scale, y * scale)
                                present = (255, 255, 255) if num in grid[y][x]["possible"] else (0, 0, 0)
                                draw.text(small_pos, str(num), font=small_font, anchor="la", fill=present)
                            draw.text(cell_pos(x, y), str(actual), font=font, anchor="mm", fill=col)
                    img.save("sugu.png")
                    img = original_image.copy()
                    draw = ImageDraw.Draw(img)
                    input("...")
        
        # should_continue = False
        for y in range(height):
            for x in range(width):
                if not grid[y][x]["found"]:
                    should_continue = True
                    continue
        # if has_guessed
        
        # pprint(grid)
        # for y in range(height):
        #     for x in range(width):
        #         current = grid[y][x]
        #         col = (100, 100, 100) if current["starter"] else (0, 0, 0)
        #         actual = current["actual"] if current["found"] else ""
        #
        #         for num in range(1, 10):
        #             small_pos = ((x + (num / 12)) * scale, y * scale)
        #             present = (255, 255, 255) if num in grid[y][x]["possible"] else (0, 0, 0)
        #             draw.text(small_pos, str(num), font=small_font, anchor="la", fill=present)
        #         draw.text(cell_pos(x, y), str(actual), font=font, anchor="mm", fill=col)
        # img.save("sugu.png")
        # pprint([grid[p[1]][p[0]] for p in get_coords_in_block(5)])
        # if GUESSING_ENABLED:
        #     input("\t" * len(guesses_stack) + ">")
        # else:
        #     input(">")
        
        old_grid = copy_grid()
        
    for y in range(height):
        for x in range(width):
            current = grid[y][x]
            col = (100, 100, 100) if current["starter"] else (0, 0, 0)
            actual = current["actual"] if current["found"] else ""

            draw.text(cell_pos(x, y), str(actual), font=font, anchor="mm", fill=col)
    
    img.save("sugu.png")


if __name__ == '__main__':
    test_blocks = [
        "112233",
        "111224",
        "567724",
        "566774",
        "556874",
        "588884"
    ]

    test_starters = { (1, 0):5, (3, 0):3, (1, 2):3, (5, 2):2, (3, 3):2 }
    
    # test_blocks = [
    #     "111122",
    #     "334122",
    #     "344452",
    #     "364555",
    #     "366758",
    #     "668888"
    # ]
    #
    # test_starters = {}
    # test_starters[(0, 1)] = 2
    # test_starters[(1, 4)] = 4
    # test_starters[(1, 5)] = 1
    # test_starters[(2, 0)] = 5
    # test_starters[(3, 5)] = 3
    # test_starters[(4, 0)] = 1
    # test_starters[(5, 4)] = 5
    #
    #
    
    solve(test_blocks, test_starters)
