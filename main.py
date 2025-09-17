#!/opt/homebrew/bin/python3
"""A script for cropping screenshots taken during Discord video calls"""

__author__ = "Charles Mesa Cayobit"

from argparse import ArgumentParser
from pathlib import Path

import cv2 as cv
import numpy as np

MAX_SCREENSHOT_HEIGHT = 2_234
MAX_SCREENSHOT_WIDTH = 3_456

MAX_CROPPED_HEIGHT = 1_850
MAX_CROPPED_WIDTH = 3_426

BLACK_BGR = np.zeros(3, np.uint8)
MIN_IMG_AREA = 50_000
MAX_IMG_AREA = MAX_CROPPED_HEIGHT * MAX_CROPPED_WIDTH

NEW_SUFFIX = "_new"
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff"}


def crop(image: Path) -> Path:
    img = cv.imread(f"{image}")
    if img is None:
        raise ValueError("Empty image")

    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    mask = cv.threshold(img_gray, 0.001, 255, cv.THRESH_BINARY)[1]

    contours = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)[0]
    contours_video: list[cv.Mat] = []
    for c in contours:
        area = cv.contourArea(c)
        if (area > MIN_IMG_AREA) and (area < MAX_IMG_AREA):
            contours_video.extend(c)

    x, y, w, h = cv.boundingRect(np.array(contours_video))
    img_cropped = img[y : y + h, x : x + w]

    new_image = image.with_stem(f"{image.stem}{NEW_SUFFIX}")
    cv.imwrite(f"{new_image}", img_cropped)

    return new_image


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="image to crop")
    args = parser.parse_args()

    if not args.image.is_file():
        raise ValueError("Not a valid file")

    new_file = crop(args.image)
    print(new_file)
