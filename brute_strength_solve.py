groups = None
width: int = None
height: int = None
number_of_blocks: int = None
block_sizes = None


def init(group_block, grid_size):
    global width, height, groups, number_of_blocks, block_sizes
    width, height = grid_size
    groups = group_block
    number_of_blocks = max([max(k) for k in groups])
    block_sizes = { }
    for y in range(height):
        for x in range(width):
            if groups[y][x] not in block_sizes:
                block_sizes[groups[y][x]] = 0
            block_sizes[groups[y][x]] += 1


def get_size_of_block(x, y):
    return block_sizes[groups[y][x]]


def find_next_cell_to_fill(grid, i, j):
    for x in range(i, width):
        for y in range(j, height):
            if grid[x][y] == 0:
                return x, y
    for x in range(0, width):
        for y in range(0, height):
            if grid[x][y] == 0:
                return x, y
    return -1, -1


def find_all_cells_in_block(index):
    out = []
    for x in range(width):
        for y in range(height):
            if groups[y][x] == index:
                out.append((x, y))
    return out


def is_valid(grid, place_at_x, place_at_y, to_place):
    get_at_cell = lambda x, y : (to_place if (x, y) == (place_at_x, place_at_y) else grid[y][x]) if (0<= x < width and 0 <= y < height) else 0
    # get_at_cell = lambda x, y:grid[y][x] if (0 <= x < width and 0 <= y < height) else 0
    for y in range(height):
        for x in range(width):
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == dy == 0: continue
                    if get_at_cell(x, y) == get_at_cell(x + dx, y + dy) != 0:
                        # print("Touching")
                        return False
            for other_cell in find_all_cells_in_block(groups[y][x]):
                if other_cell == (x, y): continue
                if get_at_cell(*other_cell) == get_at_cell(x, y) != 0:
                    # print("Same block")
                    return False
    for block_num in range(1, number_of_blocks + 1):
        block_size = block_sizes[block_num]
        for cell in find_all_cells_in_block(block_num):
            if get_at_cell(*cell) > block_size:
                # print(f"Invalid value in cell: {get_at_cell(*cell)} @ {cell}")
                return False
    return True


def solve_suguru(grid, y = 0, x = 0):
    y, x = find_next_cell_to_fill(grid, y, x)
    if y == -1:
        # print("Found end!")
        return True
    for e in range(1, get_size_of_block(y, x) + 2):
        # print(f"Testing {e} at {(i, j)}")
        if is_valid(grid, x, y, e):
            # print("Valid")
            grid[y][x] = e
            if solve_suguru(grid, y, x):
                return True
            # Undo the current cell for backtracking
            grid[y][x] = 0
        else:
            # print("Invalid!")
            pass
    return False


if __name__ == '__main__':
    test_groups = [
        [1, 1, 2, 2, 3, 3],
        [1, 1, 1, 2, 2, 4],
        [5, 6, 7, 7, 2, 4],
        [5, 6, 6, 7, 7, 4],
        [5, 5, 6, 8, 7, 4],
        [5, 8, 8, 8, 8, 4]
    ]
    
    test_start = [
        [3, 5, 0, 3, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 3, 0, 0, 0, 2],
        [0, 2, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0]
    ]
    
    from time import time
    
    init(test_groups, (6, 6))
    
    start_time = time()
    result = solve_suguru(test_start)
    end_time = time()
    
    print(f"Solving... {result=}")
    print(test_start)
    print(f"Took {end_time - start_time:.2f}s")
    print(f"{is_valid(test_start, 0, -2, 0)}")