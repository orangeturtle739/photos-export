#! /usr/bin/env python3

import json
import progressbar
import os
import sys
from argparse import ArgumentParser
from shutil import copyfile
from shutil import move


# Source_dir : passed as parameter, where your photos are located
# output_dir : directory under where all albuns will be created

def run(source_dir, output_dir):
    bar = progressbar.ProgressBar()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    num_of_missing = 0
    for f in bar(os.listdir(source_dir)):                                       # f is each file in directory
        (root_file, ext) = os.path.splitext(f)
        if ext == '.json':                                                      # only .json are treated
            with open(os.path.join(source_dir, f)) as data_file:
                data = json.load(data_file)
                number_of_albums = len(data['albums'])                          # number of albuns, to copy to various albuns
                album_counter = 1
                for album in data['albums']:                                    # list of all albuns the photo is included
                    album = album.replace("/", "_")
                    if not os.path.exists(os.path.join(output_dir, album)):
                        os.mkdir(os.path.join(output_dir, album))               # Create the albun on destination directory

                    imagename = data['path'].split(os.sep)[-1]
                    imagesource = os.path.join(source_dir, imagename)           # the file must be with the json file, copied from extract_photos.py
                    imagedestination = os.path.join(output_dir, album, imagename)


                    # temporary commented, until tested it all right, no copies, no moves.
                    if album_counter == number_of_albums:
                        if os.path.exists(imagesource):                                    # let's not consider the photo was exported or will raise an exception
                            #move(imagesource, imagedestination)       # this is the last album, so, move the file
                            print("Moving : ", imagesource, " -> ", imagedestination)
                        else:
                            print("Missing File:", imagesource)
                            num_of_missing += 1
                    else:
                        #copyfile(imagesource, imagedestination)   # temporary commented, until tested it all right, no copies, no moves.
                        print("\tCopying: ", imagesource, " -> ", imagedestination)
                        album_counter += 1

    print ("Number of missing files: ", num_of_missing)

# Usage: ./album_folder <source_dir> <output_dir>
# Copies all files from source_dir to a folder-based map structure in output_dir
# Useful for programs like Plex, who expect a folder-based structure for pictures
if __name__ == '__main__':

    # Options parsed from command line
    parser = ArgumentParser()
    parser.add_argument('source_dir', help='Path of where the .json and photos were exported')
    parser.add_argument('output_dir', help='Path to where the albuns and the files will be created/moved')

    try:
        args = parser.parse_args()
    except:
        sys.exit(2)

    run(args.source_dir, args.output_dir)
