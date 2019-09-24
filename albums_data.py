#! /usr/bin/env python3

#     This script reads ans stores all Albums seneitive  information
#  from Photos.app, used to store a Album on the right Folder it should go
#  Generates a JSON file of the information to be used later
#
import json
import progressbar
import os
import sys
import sqlite3

# SOME CONSTANTS USED
ALBUM_TABLE="RKAlbum"
FOLDER_TABLE="RKFolder"

UUID_FIELD="uuid"
NAME_FIELD="name"
TRASH_FIELD="isInTrash"
MODELID_FIELD="modelId"

FOLDER_FIELD="folderUuid"


# Ignore all albuns inside these folders. consider only user created
IGNORED_FOLDERS_ALBUNS = ['LibraryFolder', 'TopLevelAlbums', 'MediaTypesSmartAlbums', 'TopLevelSlideshows', 'TrashFolder']
JSON_FILENAME="albums.json"

# helper function, to debug
#def print_dict(dicionario):
#   print("--  Dicionario: --")
#    for key, val in dicionario.items():
#        print(key, "=>", val)
#    print("----------------------------------")


def run(lib_dir, output_dir):
    db_path = os.path.join(lib_dir, 'database')
    main_db_path = os.path.join(db_path, 'photos.db')

    main_db = sqlite3.connect(main_db_path)
    main_db.row_factory = sqlite3.Row

    # Get all albums information
    album_table = main_db.cursor()
    album_table.execute('SELECT * FROM ' + ALBUM_TABLE)

    # will store uuid -> [name, folder]
    db_album_dict = {}

    # let's test each album
    for album in iter(album_table.fetchone, None):
        # Ignore Trashed albums
        if album[TRASH_FIELD] == 1:
            continue

        album_name      = album[NAME_FIELD]
        album_uuid      = album[UUID_FIELD]
        album_folder    = album[FOLDER_FIELD]
        album_modelid   = album[MODELID_FIELD]

        # add to dictionary
        if album_folder not in IGNORED_FOLDERS_ALBUNS and album_name != None:
            #album_name = album_name.replace('/', '_')
            db_album_dict[album_uuid] = [album_name, album_folder]

    #print_dict(db_album_dict)

    #  mount and store final JSON on file
    json_albums = json.dumps(db_album_dict)
    json_path = os.path.join(output_dir, JSON_FILENAME)
    json_file = open(json_path, "w")
    json_file.write(json_albums)
    json_file.close()



# Usage: ./folder_structure.py <photo_library> <output_dir>
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
