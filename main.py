"""A script for cropping screenshots taken during Discord video calls"""

__author__ = "Charles Mesa Cayobit"


from argparse import ArgumentParser
from pathlib import Path

from crop_discord_call_photos import main

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", type=Path, help="directory containing images to crop"
    )
    args = parser.parse_args()

    main(args.directory)
