#! /usr/bin/env python3

import clean_albums
import extract_photos
import set_exif
import albums_data
import folder_structure
import group_versions
import album_folder
import sys
from argparse import ArgumentParser


def output(thing):
    print('>>> %s' % thing)


def askyesno():
    answer = None
    while answer not in ("yes", "no"):
        answer = input("Enter yes or no: ")
        if answer == "yes":
            return True
        elif answer == "no":
            return False
        else:
            print("Please enter yes or no.")


def run(lib_dir, output_dir, digikam_dir):
    temp_dir = os.path.join(output_dir, "temporaryfolder")

    output('Extracting photos')
    extract_photos.run(lib_dir, temp_dir)

    output('Cleaning album names')
    clean_albums.run(temp_dir)

    output('Setting EXIF metadata')
    set_exif.run(temp_dir)

    if digikam_dir is not None:
        output('Grouping Versions...')
        group_versions.run(digikam_dir, temp_dir)

    output('Exporting Folder Structure')
    folder_structure.run(lib_dir, temp_dir)

    output('Exporting Albums Structure Information')
    albums_data.run(lib_dir, temp_dir)

    output('Moving Photos to final destination.')
    album_folder.run(temp_dir, output_dir)


# Usage: ./photos_export.py <photo_library> <output_dir> <digikam_dir>
# digikam_dir may be any dir, if you want to ignore it.
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'photoslib_dir',
        help='Path of where the .json and photos were exported')
    parser.add_argument(
        'output_dir',
        help='Path to where the albums and the files will be created/moved')
    parser.add_argument('digikamdb_dir', nargs='?',
                        help='Path to where Digikam DB is located')

    try:
        args = parser.parse_args()
    except Exception as error:
        print("Argument error: ", error)
        sys.exit(2)

    # run(sys.argv[1], sys.argv[2], sys.argv[3])
    run(args.photoslib_dir, args.output_dir, args.digikamdb_dir)
