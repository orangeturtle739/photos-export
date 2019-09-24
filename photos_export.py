#! /usr/bin/env python3

import clean_albums
import extract_photos
import set_exif
import sys


def output(thing):
    print('>>> %s' % thing)


def run(lib_dir, output_dir):
    output('Extracting photos')
    extract_photos.run(lib_dir, output_dir)
    output('Cleaning album names')
    clean_albums.run(output_dir)
    output('Setting EXIF metadata')
    set_exif.run(output_dir)


# Usage: ./photos_export.py <photo_library> <output_dir>
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
