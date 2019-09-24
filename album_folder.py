#! /usr/bin/env python3

import json
import progressbar
import os
import sys
import time
import datetime
from argparse import ArgumentParser
from shutil import copyfile
from shutil import move

SYSTEM_FILES = ["albums.json", "folders.json"]

# Source_dir : passed as parameter, where your photos are located
# output_dir : directory under where all albuns will be created
def run(source_dir, output_dir, verbose):
    def vprint(x):
        if verbose:
            print(x)

    bar = progressbar.ProgressBar()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Let's print some statistics
    num_of_missing = 0
    num_of_albuns = 0
    num_of_copied = 0
    num_of_moved = 0
    num_of_json = 0

    all_files = os.listdir(source_dir)
    num_of_total_files = len(all_files)

    # load albums and folders data file
    albums_path = os.path.join(source_dir, SYSTEM_FILES[0])
    folders_path = os.path.join(source_dir, SYSTEM_FILES[1])

    try:
        albums_file = open(albums_path)
        albums_dict = json.load(albums_file)

        folders_file = open(folders_path)
        folders_dict = json.load(folders_file)
    except:
        print("Error loading Albums or Folders system file.\n\t", albums_path, folders_path)
        sys.exit(1)

    for f in bar(all_files):
        (root_file, ext) = os.path.splitext(f)
        filename = os.path.basename(f)
        if ext != '.json' or filename in SYSTEM_FILES:
            continue

        num_of_json += 1
        with open(os.path.join(source_dir, f)) as data_file:
            data = json.load(data_file)
            album_counter = 1

            # This is the physical exported file
            file_exported_name = data['uuid']
            # This is the ORIGINAL file name
            file_original_name = os.path.basename(
                data['path'])
            # get Extension of photo file
            root, file_extension = os.path.splitext(
                file_original_name)
            # the file must be located with the json file, copied from
            # extract_photos.py
            imagesource = os.path.join(
                source_dir,
                file_exported_name +
                file_extension.lower())

            # Some photos do no have any albums included in. So, on those cases,
            # we have just to copy to destination dir.
            # Those photos whose have albuns, will be treated later
            # number of albums, to copy to various albums
            number_of_albums = len(data['albums'])
            if number_of_albums == 0:
                # destination without album
                imagedestination = os.path.join(output_dir, file_original_name)
                if os.path.exists(imagesource):
                    vprint('Moving : {} -> {}'.format(imagesource, imagedestination))
                    # this is the last album, so, move the file
                    move(imagesource, imagedestination)
                    num_of_moved += 1
                else:
                    vprint('Missing File: {}'.format(imagesource))
                    num_of_missing += 1
            # this is where the photo is included in some album
            else:
                # get the list of all albums UUIDs the photo is included
                for album_id in data['albums']:
                    album_name = albums_dict[album_id][0]
                    album_name = album_name.replace(os.path.sep, '_')

                    # mount the final path of the Album, based in its UUID.
                    # get the folder path from folders dict
                    folder_id = albums_dict[album_id][1]
                    album_folder = folders_dict[folder_id][1]

                    album_fullpath = os.path.join(output_dir, album_folder, album_name)

                    if not os.path.exists(album_fullpath):
                        # Create the album on destination directory
                        os.makedirs(album_fullpath, exist_ok=True)
                        num_of_albuns += 1

                    imagedestination = os.path.join(album_fullpath, file_original_name)   # change destination to inside album

                    if album_counter == number_of_albums:
                        # let's not consider the photo was exported or will
                        # raise an exception
                        if os.path.exists(imagesource):
                            vprint(
                                'Moving : {} -> {}'.format(imagesource, imagedestination))
                            # this is the last album, so, move the file
                            move(imagesource, imagedestination)
                            num_of_moved += 1
                        else:
                            vprint('Missing File: {}'.format(imagesource))
                            num_of_missing += 1
                    else:
                        if args.verbose:
                            vprint(
                                'Copying: {} -> {}'.format(imagesource, imagedestination))
                        # no copies, no moves.
                        copyfile(imagesource, imagedestination)
                        album_counter += 1
                        num_of_copied += 1

    vprint('Total files to process: {}'.format(num_of_total_files))
    vprint('JSON files: {}'.format(num_of_json))
    vprint('Number of missing files: {}'.format(num_of_missing))
    vprint('Total albums created: {}'.format(num_of_albuns))
    vprint('Total files moved: {}'.format(num_of_moved))
    vprint('Total files duplicated to albuns: {}'.format(num_of_copied))

# Usage: ./album_folder <source_dir> <output_dir>
# Copies all files from source_dir to a folder-based map structure in output_dir
# Useful for programs like Plex, who expect a folder-based structure for
# pictures
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Turn on processing of each file')
    parser.add_argument(
        'source_dir',
        help='Path of where the .json and photos were exported')
    parser.add_argument(
        'output_dir',
        help='Path to where the albuns and the files will be created/moved')

    try:
        args = parser.parse_args()
    except:
        sys.exit(2)

    start_time = time.time()
    run(args.source_dir, args.output_dir, args.verbose)
    end_time = time.time()

    print("-----  Time of processing: {}  -----".format(
        datetime.timedelta(seconds=end_time - start_time)))
