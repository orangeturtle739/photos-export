#! /usr/bin/env python3

import clean_albums
import extract_photos
import set_exif
import albums_data
import folder_structure
import group_versions
import album_folder
import sys


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

def run(lib_dir, output_dir):
    temp_dir = os.path.join(output_dir, "temporaryfolder")

    output('Extracting photos')
    extract_photos.run(lib_dir, temp_dir)

    output('Cleaning album names')
    clean_albums.run(temp_dir)

    output('Setting EXIF metadata')
    set_exif.run(temp_dir)

    output("ONLY FOR DIGIKAM USERS !\nDo you want to Group Versions ? You need to run Digikam and configure repository first !")
    if askyesno():
        output('Setting EXIF metadata')
        group_versions.run(temp_dir)

    output('Exporting Folder Structure')
    folder_structure.run(lib_dir, temp_dir)

    output('Exporting Albums Structure Information')
    albums_data.run(lib_dir, temp_dir)

    output('Moving Photos to final destination.')
    album_folder.run(temp_dir, output_dir)



# Usage: ./photos_export.py <photo_library> <output_dir>
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
