#! /usr/bin/env python3

#     This script reads Folder structure from Photos.app
#  and generates a JSON file to be reproduced on export, creating
#  a structure identical with the albuns inside it.
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

ALBUM_FOLDER_FIELD="folderUuid"
FOLDER_PATH_FIELD="folderPath"
FOLDER_MODELID="modelId"

IGNORED_FOLDERS = ['LibraryFolder', 'TopLevelAlbums', 'MediaTypesSmartAlbums', 'TopLevelSlideshows', 'TrashFolder']
JSON_FILENAME="folders.json"

#def print_dict(dicionario):
#    print("--  Dicionario: --")
#    for key, val in dicionario.items():
#        print(key, "=>", val)
#    print("----------------------------------")


def split_path(path):
    folders = path.split('/')
    return folders


def run(lib_dir, output_dir):
    db_path = os.path.join(lib_dir, 'database')
    main_db_path = os.path.join(db_path, 'photos.db')

    main_db = sqlite3.connect(main_db_path)
    main_db.row_factory = sqlite3.Row

    # PASSO1: Pega a tabela de todas as pastas
    folders_table = main_db.cursor()
    folders_table.execute('SELECT * FROM ' + FOLDER_TABLE)

    # will store modelID -> [FOLDERNAME, PATH]
    db_folder_dict = {}

    # PASSO2: Para cada pasta listada,
    for folder in iter(folders_table.fetchone, None):
        # Ignore Trashed Folders
        if folder[TRASH_FIELD] == 1:
            continue

        folder_path     = folder[FOLDER_PATH_FIELD]
        folder_name     = folder[NAME_FIELD]
        folder_uuid     = folder[UUID_FIELD]
        folder_modelid  = folder[FOLDER_MODELID]

        # add to dictionary
        #print("Adicionando... KEY/UUID/NAME/PATH", folder_modelid, folder_uuid, folder_name, folder_path)
        db_folder_dict[folder_modelid] = [folder_uuid, folder_name, folder_path]

    # Dict ready. Let's substitute the Paths and return a simpler dict
    final_dict = {}
    for key,val in db_folder_dict.items():
        path_numbered = val[2]                          # get the path in numbers
        key_uuid = val[0]                            # the key for the final dict
        name = val[1]

        path_described = ""
        for number in path_numbered.split('/'):
            if number != "":                     # the last will always be empty, ignore
                int_number = int(number)
                folder_name = db_folder_dict[int_number][1]
                folder_uuid = db_folder_dict[int_number][0]
                if folder_uuid not in IGNORED_FOLDERS:
                    if path_described != "":
                        path_described += os.path.sep

                    path_described += folder_name   # Change folder number to Folder name
                    final_dict[key_uuid] = [name, path_described]

    #  mount and store final JSON on file
    json_folders = json.dumps(final_dict)
    json_path = os.path.join(output_dir, JSON_FILENAME)
    json_file = open(json_path, "w")
    json_file.write(json_folders)
    json_file.close()



# Usage: ./folder_structure.py <photo_library> <output_dir>
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
