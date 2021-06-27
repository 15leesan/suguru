from typing import List, Tuple, Dict
import cv2
import pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

Coordinate = Tuple[int, int]
grid_size: Tuple[int] = tuple()

DEBUG = False


blocks = []


def set_block(block):
    global blocks
    blocks = block


def split(file_path) -> Dict[Coordinate, np.ndarray]:
    im: np.ndarray = cv2.imread(file_path)
    cell_size = (round(im.shape[0] / grid_size[0]), round(im.shape[1] / grid_size[1]))
    cells = {}
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            cell = im[y * cell_size[1]:(y + 1) * cell_size[1], x * cell_size[0]:(x + 1) * cell_size[0]]
            # cell = im.crop((x * cell_size[0], y * cell_size[1], (x + 1) * cell_size[0], (y + 1) * cell_size[1]))
            cells[(x, y)] = cell
    return cells


def set_starters_grid_size(grid_x, grid_y):
    global grid_size
    grid_size = (grid_x, grid_y)


def show_parts(file_path, grid_x, grid_y) -> Dict[Coordinate, int]:
    global grid_size
    grid_size = (grid_x, grid_y)
    sections = split(file_path)
    
    starters: Dict[Coordinate, int] = {}
    
    for y in range(grid_y):
        for x in range(grid_x):
            im: np.ndarray = sections[(x, y)]
            # Alternatively: can be skipped if you have a Blackwhite image
            gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
            _, img_bin = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            gray: np.ndarray = cv2.bitwise_not(img_bin)
            cell_x, cell_y = gray.shape[0:2]
            margin = round(cell_x / 7.5)
            gray = gray[margin:-margin, margin:-margin]
            if DEBUG:
                cv2.imshow("a", gray)
            kernel = np.ones((2, 1), np.uint8)
            img = cv2.erode(gray, kernel, iterations=1)
            img = cv2.dilate(img, kernel, iterations=1)
            out_below = pytesseract.image_to_string(img, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789 -c page_separator=""').strip()
            
            if len(out_below) > 0:
                starters[(x, y)] = int(out_below)
            
            if DEBUG:
                print(f"({out_below}), {len(out_below)=}")
                cv2.waitKey()
    cv2.destroyWindow("a")
    # cv2.imwrite("single_cell.png", im)
    return starters


def resolve(starters):
    original_image: np.ndarray = np.full((grid_size[1] + 2, grid_size[0] + 2, 3), 255, np.uint8)
    SCALE = 48
    image_pos = lambda x, y: ((x + 1) * SCALE, (y + 1) * SCALE)
    original_image = cv2.resize(original_image, (original_image.shape[0] * SCALE, original_image.shape[1] * SCALE))
    for x in range(grid_size[0] + 1):
        cv2.line(original_image, image_pos(x, 0), image_pos(x, grid_size[1]), (0, 0, 0), 1)
    for y in range(grid_size[1] + 1):
        cv2.line(original_image, image_pos(0, y), image_pos(grid_size[0], y), (0, 0, 0), 1)
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            current = blocks[y][x]
            # Up
            if y == 0:
                cv2.line(original_image, image_pos(x, y), image_pos(x + 1, y), (0, 0, 0), 3)
            elif blocks[y - 1][x] != current:
                cv2.line(original_image, image_pos(x, y), image_pos(x + 1, y), (0, 0, 0), 3)
        
            # Down
            if y == grid_size[1] - 1:
                cv2.line(original_image, image_pos(x, y + 1), image_pos(x + 1, y + 1), (0, 0, 0), 3)
        
            # Left
            if x == 0:
                cv2.line(original_image, image_pos(x, y), image_pos(x, y + 1), (0, 0, 0), 3)
            elif blocks[y][x - 1] != current:
                cv2.line(original_image, image_pos(x, y), image_pos(x, y + 1), (0, 0, 0), 3)
        
            # Right
            if x == grid_size[0] - 1:
                cv2.line(original_image, image_pos(x + 1, y), image_pos(x + 1, y + 1), (0, 0, 0), 3)
    selection = (0, 0)
    while True:
        im = original_image.copy()
        
        cv2.rectangle(im, image_pos(selection[0], selection[1]), image_pos(selection[0] + 1, selection[1] + 1), (0, 0, 255), 3)
        for pos in starters:
            to_pos = image_pos(pos[0], pos[1] + 1)
            to_pos = to_pos[0] + 10, to_pos[1] - 10
            cv2.putText(im, str(starters[pos]), to_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
        cv2.imshow("Rewrite", im)
        k = cv2.waitKey()
        if k == 27 or k == 13:
            # ESC pressed
            cv2.destroyWindow("Rewrite")
            return starters
        elif k == 100:
            selection = selection[0] + 1, selection[1]
        elif k == 97:
            selection = selection[0] - 1, selection[1]
        elif k == 119:
            selection = selection[0], selection[1] - 1
        elif k == 115:
            selection = selection[0], selection[1] + 1
        elif k in [8, 32, 48]:
            if selection in starters:
                del starters[selection]
        elif 49 <= k <= 57:
            starters[selection] = k - 48
        
        selection = min(max(selection[0], 0), grid_size[0] - 1), min(max(selection[1], 0), grid_size[1] - 1)
