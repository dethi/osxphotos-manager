#!/usr/bin/env python3

import os
from collections import defaultdict
from operator import itemgetter

import argparse
import humanize
import osxphotos


def _get_system_library_path():
    return osxphotos.utils.get_system_library_path() or os.path.expanduser(
        "~/Pictures/Photos Library.photoslibrary"
    )


def get_system_library():
    return osxphotos.PhotosDB(_get_system_library_path())


def group_by_month(photos):
    buckets = defaultdict(list)  # {year-month: [photos]}
    for photo in photos:
        buckets[photo.date.strftime("%Y-%m")].append(photo)

    return buckets


def total_size_by(buckets):
    return {
        k: sum(os.stat(p.path).st_size for p in photos if p.path)
        for k, photos in buckets.items()
    }


def main(sort_by_size):
    photos = get_system_library().photos()

    photos_by_month = group_by_month(photos)
    total_size_by_month = total_size_by(photos_by_month)

    key_func = itemgetter(1 if sort_by_size else 0)
    for k, size in sorted(total_size_by_month.items(), key=key_func):
        print(f"{k} --> {humanize.naturalsize(size)}")

    total_size = sum(total_size_by_month.values())
    print("---")
    print(f"Total size: {humanize.naturalsize(total_size)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--by-size", help="sort output by size instead of month", action="store_true",
    )
    args = parser.parse_args()

    main(args.by_size)
