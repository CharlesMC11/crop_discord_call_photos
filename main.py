#!/opt/homebrew/bin/python3
"""A script for cropping screenshots taken during Discord video calls"""

__author__ = "Charles Mesa Cayobit"

from argparse import ArgumentParser
from pathlib import Path

import cv2 as cv
import numpy as np

BLACK_BGR = np.zeros(3, np.uint8)
MIN_IMG_AREA = 1 << 16
MAX_IMG_AREA = 1 << 22

NEW_SUFFIX = "_new"

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def crop(image: Path) -> Path:
    # TODO: Check image resolution first before pre-cropping?
    img = cv.imread(f"{image}")[256:-64, 512:-64]
    try:
        mask = cv.inRange(img, BLACK_BGR, BLACK_BGR)
    except cv.error:
        raise ValueError("Empty image")

    contours = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)[0]
    contours_video = []
    for c in contours:
        area = cv.contourArea(c)
        if (area > MIN_IMG_AREA) and (area < MAX_IMG_AREA):
            contours_video.extend(c)

    x, y, w, h = cv.boundingRect(np.array(contours_video))
    img_cropped = img[y + 1 : y + h - 1, x + 1 : x + w - 1]

    new_image = image.with_stem(f"{image.stem}{NEW_SUFFIX}")
    cv.imwrite(f"{new_image}", img_cropped)

    return new_image


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="image to crop")
    args = parser.parse_args()

    new_file = crop(args.image)
    print(new_file)
