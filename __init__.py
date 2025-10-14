__author__ = "Charles Mesa Cayobit"

import subprocess
import tarfile
from collections.abc import Iterator
from pathlib import Path
from warnings import warn

import cv2 as cv
import numpy as np

MAX_SCREENSHOT_HEIGHT = 2_234
MAX_SCREENSHOT_WIDTH = 3_456

MAX_CROPPED_HEIGHT = 1_850
MAX_CROPPED_WIDTH = 3_426

BLACK_BGR = np.zeros(3, np.uint8)
MIN_IMG_AREA = 50_000
MAX_IMG_AREA = MAX_CROPPED_HEIGHT * MAX_CROPPED_WIDTH

_NEW_IDENTIFIER = "cropped_"
IMAGE_EXTENSIONS = {"heif", "jpeg", "jpg", "png", "tif", "tiff"}

DEFAULT_SCREENSHOT_EXT = "png"
FILENAME_PATTERN = "[1-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]"


def crop(image: Path, new_affix: str = _NEW_IDENTIFIER) -> Path:
    """Crop an image with a black background.

    :param image: Path to the image to crop.
    :param new_affix: Affix for cropped image’s filename.
    :return: Path to the cropped image.
    :raises: ValueError if the provided image is empty.
    """

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

    new_image = image.with_stem(f"{new_affix}{image.stem}")
    cv.imwrite(f"{new_image}", img_cropped)

    return new_image


def clean_up(
    directory: Path,
    images: dict[Path, Path],
    file_extension: str = DEFAULT_SCREENSHOT_EXT,
) -> None:
    """Copy the original images’ metadata onto the cropped ones, then archive the originals.

    :param directory: Directory containing the images.
    :param images: A map between an original image and its cropped version.
    :param file_extension: The images’ file extension.
    """

    exiftool_args: list[str | Path] = [
        "exiftool",
        "-tagsFromFile",
        f"%-13f.{file_extension}",
        "-all<all",
        "-MaxAvailWidth<ImageWidth",
        "-MaxAvailHeight<ImageHeight",
        "-extension",
        file_extension,
        "-ignoreMinorErrors",
        "-overwrite_original",
        "-preserve",
        "-quiet",
        "--",
    ]
    exiftool_args.extend(images.values())
    subprocess.run(exiftool_args, cwd=directory)

    with tarfile.open(directory / "originals.tar.gz", "w:gz", compresslevel=1) as tar:
        for f in images:
            tar.add(f, arcname=f.name)

    for orig, cropped in images.items():
        cropped.replace(orig)


def main(
    directory: Path,
    filename_pattern: str = FILENAME_PATTERN,
    file_extension: str = DEFAULT_SCREENSHOT_EXT,
) -> None:
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    files: Iterator[Path] = directory.glob(f"{filename_pattern}.{file_extension}")

    # Map of original images to their cropped version
    processed_successfully: dict[Path, Path] = {}
    for image in files:
        try:
            processed_successfully[image] = crop(image)
        except ValueError as e:
            warn(f"{e}")
            continue
        except Exception:
            raise

    if not processed_successfully:
        RuntimeError("No files processed")

    clean_up(directory, processed_successfully, file_extension)
