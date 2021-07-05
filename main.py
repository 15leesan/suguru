from extract import get_with_camera
from find_lines import get_block_shapes, set_grid_size, set_threshold, get_thick_lines
from suguru_solver import solve
from find_starters import show_parts, resolve, set_starters_grid_size, set_block
import cv2

if __name__ == '__main__':
    skewed = get_with_camera()
    cv2.imwrite("target.png", skewed)
    # size = input("Enter grid size (width x height): ")
    size = ""
    if len(size) > 0:
        grid_x, grid_y = [int(k.strip()) for k in size.split("x")]
    else:
        grid_x, grid_y = (6, 6)

    set_grid_size(grid_x, grid_y)
    
    threshold = 95
    while True:
        blocks = get_block_shapes("target.png")
        im = cv2.imread("lines.png")
        cv2.imshow("Lines", im)
        k = cv2.waitKey()
        if k in [27, 13, 32]: break
        elif k == 119: threshold += 5
        elif k == 115: threshold -= 5
        set_threshold(threshold)

    passthrough_blocks = blocks.splitlines()
    passthrough_blocks = [[int(i) for i in line.split(".")] for line in passthrough_blocks]
    thicks = get_thick_lines()
    set_block(passthrough_blocks)
    cv2.destroyWindow("Lines")
    print(blocks)
    print(passthrough_blocks)
    
    # set_starters_grid_size(grid_x, grid_y)
    starters = show_parts("target.png", grid_x, grid_y)
    # starters = {(1, 0): 5, (5, 0): 3, (0, 2): 3, (3, 2): 5, (2, 3): 4, (0, 5): 4}
    
    starters = resolve(starters)
    print(starters)
    
    solve(passthrough_blocks, starters)
    
    im = cv2.imread("sugu.png")
    cv2.imshow("Finished", im)
    cv2.waitKey()
