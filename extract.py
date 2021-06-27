import cv2
import numpy as np
from fpp.fpp import four_point_transform

CONST_COEFF = 0.02


def get_major_contour(original_image: np.ndarray):
    img = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
    img = cv2.medianBlur(img, 5)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    img = cv2.bitwise_not(img, img)
    # cv2.imshow("Thresholded", img)
    kernel = np.empty((5, 5), 'uint8')
    k = [
        "00100",
        "01110",
        "11211",
        "01110",
        "00100"
    ]
    for i, line in enumerate(k):
        for j, char in enumerate(line):
            kernel[i][j] = int(char)
    
    dilated = cv2.dilate(img, kernel)
    # cv2.imshow("Dilated", dilated)
    (contours, _) = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    screenCnt = None
    maxPerimeter = 0
    
    for contour in contours:
        o = original_image.copy()
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, CONST_COEFF * perimeter, True)
        if len(approx == 4): break
    
    screenCnt = approx
    maxPerimeter = perimeter
    return screenCnt, maxPerimeter


def get_with_camera():
    cam = cv2.VideoCapture(0)
    img_counter = 0
    transformed = None
    focus = 5
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        width, height = frame.shape[0:2]
        if height == 800 or width == 600:
            to_width, to_height = width, height
        elif height < width:
            to_width, to_height = (round(width / height * 800), 800)
        else:
            to_width, to_height = (600, round(width / height * 600))
        im = cv2.resize(frame, (to_width, to_height), interpolation=cv2.INTER_CUBIC)
        contour, perimeter = get_major_contour(im)
        points = []
        for i in contour:
            points.append(i[0])
        points = np.array(points)
        out = four_point_transform(im, points)
        out = cv2.resize(out, (out.shape[0], out.shape[0]), interpolation=cv2.INTER_CUBIC)
        
        cv2.drawContours(im, [contour], -1, (0, 255, 0), 3)
        cv2.imshow("Camera [live]", im)
        
        cv2.imshow(f"Transformed", out)
        k = cv2.waitKey(1)
        if k % 256 == 32:
            # SPACE pressed
            transformed = out
            break
        if k == 119:
            focus += 5
        elif k == 115:
            focus -= 5
        if focus < 0: focus = 0
        if focus > 255: focus = 255
        cam.set(28, focus)

    cam.release()
    cv2.destroyAllWindows()
    
    return transformed


if __name__ == "__main__":
    get_with_camera()
