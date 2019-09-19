#! /usr/bin/env python3

import json
import progressbar
import os
import sys
from shutil import copyfile

def run(source_dir, output_dir):
    bar = progressbar.ProgressBar()
    for f in bar(os.listdir(source_dir)):
        if os.path.splitext(f)[1] == '.json':
            with open(os.path.join(source_dir, f)) as data_file:
                data = json.load(data_file)
                for album in data['albums']:
                    album = album.replace("/", "_")
                    if not os.path.exists(os.path.join(output_dir, album)):
                        os.mkdir(os.path.join(output_dir, album))

                    imagesource = data['path']
                    imagename = data['path'].split(os.sep)[-1]
                    imagedestination = os.path.join(output_dir, album, imagename)

                    copyfile(imagesource, imagedestination)

# Usage: ./album_folder <source_dir> <output_dir>
# Copies all files from source_dir to a folder-based map structure in output_dir
# Useful for programs like Plex, who expect a folder-based structure for pictures
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
