#! /usr/bin/env python3

import json
import progressbar
import os
import sys
import time
from argparse import ArgumentParser
from shutil import copyfile
from shutil import move


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
    num_of_total_files = 0
    num_of_json = 0

    all_files = os.listdir(source_dir)
    num_of_total_files = len(all_files)

    for f in bar(all_files):
        (root_file, ext) = os.path.splitext(f)
        if ext != '.json':
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
                # list of all albums the photo is included
                for album in data['albums']:
                    album = album.replace('/', '_')
                    if not os.path.exists(os.path.join(output_dir, album)):
                        # Create the album on destination directory
                        os.mkdir(os.path.join(output_dir, album))
                        num_of_albuns += 1

                    imagedestination = os.path.join(
                        output_dir, album, file_original_name)   # change destination to inside album

                    # temporary commented, until tested it all right, no
                    # copies, no moves.
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
