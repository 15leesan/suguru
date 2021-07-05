# suguru

A suguru is a form of logic puzzle, somewhat akin to a Sudoku. 

The rules for how numbers can be placed in the grid are as follows:

1. Numbers cannot be placed next to other copies of themselves. This is true horizontally, vertically and diagonally, and can be thought of an "anti-king's move constraint".
1. Each shape formed of bold lines, called a "cage", cannot contain the same number twice.
1. A cage must contain every number from 1 up to the number of squares in the cage. For example, a cage with five cells must contain the numbers 1, 2, 3, 4 and 5.

For more information, or to have a go yourself, you can use [Krazydad's interactive Suguru](https://krazydad.com/tablet/suguru/) for an online version of the game.

This is a program designed to solve suguru puzzles, (in an ideal run) nearly fully automatic, using an attached camera. It uses logical rules to eliminate possibilities in cells, but falls back to a recursive backtracking brute-force solver once it detects that no further progress can be made without guessing.

You are free to use this program as part of something else without restriction, though linking to this repo would be appreciated.

## Setup

1. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) on your system, ensuring that it can be run with the `tesseract` command, or noting down the installation path otherwise
1. Run `pip install -r requirements.txt` in a command line

## Usage

1. Run main.py, and wait for the OpenCV windows to appear
1. Hold a printed suguru (or a suguru displayed on a phone) up to the camera
1. Press space/escape/enter when the boundaries are detected correctly
    - Use the W/S keys to adjust camera focus, if supported
1. A window will appear showing the detected boundaries of the suguru
    - Use the W/S keys to adjust the threshold for thick lines - ensure that all blocks contain cells with the same color dots!
    - Press space/escape/enter to continue
1. The OCR process will now run - the next window will allow for verification and adjustment of the starting digits
    - Use the WASD keys to change the targeted cell
    - Use the numeric keys (1-9) to set the digit in the selected cell
    - Use backspace/space/0 to clear the current cell
    - Use escape once finished
1. The solver will now run, and a new window will pop up containing the final result
    - Any key to exit
    - The solution is also saved as `sugu.png`

This has been tested with quite a few different 6x6 sugurus, but has not been tested with everything it can theoretically deal with. A list of untested-but-probably-working things is below:
- [ ] Larger sugurus
- [ ] Smaller sugurus
- [ ] Non-square sugurus
- [ ] Sugurus with more than 9 cages
- [ ] Sugurus where cages are bigger than 5 cells
- [ ] Sugurus with multiple possible solutions
- [ ] Sugurus with no starting digits

## Acknowledgements

This program uses the [four-point perspective](https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py) transform from [jrosebr1/imutils](github.com/jrosebr1/imutils)

Big thanks to the [PyImageSearch](https://www.pyimagesearch.com/2020/08/10/opencv-sudoku-solver-and-ocr/) article on an OpenCV Sudoku solver for the image extraction algorithm.

