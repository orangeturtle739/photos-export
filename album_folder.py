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

def run(source_dir, output_dir):
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

    for f in bar(all_files):                                       # f is each file in directory
        (root_file, ext) = os.path.splitext(f)
        if ext == '.json':                                                      # only .json are treated
            num_of_json += 1
            with open(os.path.join(source_dir, f)) as data_file:
                data = json.load(data_file)
                album_counter = 1

                file_exported_name = data['uuid']                               # This is the physical exported file
                file_original_name = os.path.basename(data['path'])             # This is the ORIGINAL file name
                root, file_extension = os.path.splitext(file_original_name)     # get Extension of photo file
                imagesource = os.path.join(source_dir, file_exported_name + file_extension.lower())      # the file must be located with the json file, copied from extract_photos.py

                #   Some photos do no have any albums included in. So, on those cases,
                # we have just to copy to destination dir.
                #   Those photos whose have albuns, will be treated later
                number_of_albums = len(data['albums'])                          # number of albums, to copy to various albums
                if number_of_albums == 0:
                    imagedestination = os.path.join(output_dir, file_original_name)    # destination without album
                    if os.path.exists(imagesource):  # let's not consider the photo was exported or will raise an exception
                        if args.verbose:
                            print("Moving : ", imagesource, " -> ", imagedestination)
                        move(imagesource, imagedestination)       # this is the last album, so, move the file
                        num_of_moved += 1
                    else:
                        if args.verbose:
                            print("Missing File:", imagesource)
                        num_of_missing += 1
                else:                                                               # this is where the photo is included in some album
                    for album in data['albums']:                                    # list of all albums the photo is included
                        album = album.replace("/", "_")
                        if not os.path.exists(os.path.join(output_dir, album)):
                            os.mkdir(os.path.join(output_dir, album))               # Create the album on destination directory
                            num_of_albuns += 1

                        imagedestination = os.path.join(output_dir, album, file_original_name)   # change destination to inside album

                        # temporary commented, until tested it all right, no copies, no moves.
                        if album_counter == number_of_albums:
                            if os.path.exists(imagesource):                                    # let's not consider the photo was exported or will raise an exception
                                if args.verbose:
                                    print("Moving : ", imagesource, " -> ", imagedestination)
                                move(imagesource, imagedestination)       # this is the last album, so, move the file
                                num_of_moved +=1
                            else:
                                if args.verbose:
                                    print("Missing File:", imagesource)
                                num_of_missing += 1
                        else:
                            if args.verbose:
                                print("\tCopying: ", imagesource, " -> ", imagedestination)
                            copyfile(imagesource, imagedestination)   # temporary commented, until tested it all right, no copies, no moves.
                            album_counter += 1
                            num_of_copied += 1

    if args.verbose:
        print("\nTotal files to process:", num_of_total_files)
        print("JSON files:", num_of_json)
        print ("Number of missing files: ", num_of_missing)
        print("Total albums created : ", num_of_albuns)
        print("Total files moved: ", num_of_moved)
        print("Total files duplicated to albuns: ", num_of_copied)

# Usage: ./album_folder <source_dir> <output_dir>
# Copies all files from source_dir to a folder-based map structure in output_dir
# Useful for programs like Plex, who expect a folder-based structure for pictures
if __name__ == '__main__':

    # Options parsed from command line
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Turn on processing of each file')
    parser.add_argument('source_dir', help='Path of where the .json and photos were exported')
    parser.add_argument('output_dir', help='Path to where the albuns and the files will be created/moved')

    try:
        args = parser.parse_args()
    except:
        sys.exit(2)

    start_time = time.time()
    run(args.source_dir, args.output_dir)
    end_time = time.time()

    hours, rem = divmod(end_time-start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("-----  Time of processing: {:0>2}:{:0>2}:{:05.2f}   -----".format(int(hours),int(minutes),seconds))
