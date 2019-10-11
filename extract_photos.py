#! /usr/bin/env python3

import sys
import os
import sqlite3
import json
import progressbar
import shutil

global count

# Generates a unique suffix
def gen_name():
    count = 0
    while True:
        path = yield
        original_name = os.path.splitext(
            os.path.basename(path))[0]
        name = '%s_%010d' % (original_name.replace(' ', '_'), count)
        count += 1
        yield name


# Generates a unique suffix
def next_name(path, namer):
    next(namer)
    return namer.send(path)


# Does the export process, copying photos from lib_dir to output_dir
# with all metadata in a sidecar JSON


def run(lib_dir, output_dir):
    db_path = os.path.join(lib_dir, 'database')
    main_db_path = os.path.join(db_path, 'photos.db')
    proxy_db_path = os.path.join(db_path, 'photos.db')

    main_db = sqlite3.connect(main_db_path)
    main_db.row_factory = sqlite3.Row
    proxy_db = sqlite3.connect(proxy_db_path)
    proxy_db.row_factory = sqlite3.Row

    namer = gen_name()

    # Map below doesn't seem to exist anymore. Leaving this here in case
    # someone finds it.

    # edited_root = os.path.join(lib_dir, 'resources', 'modelresources')
    # edited_index = {}

    # for subdir, dirs, files in os.walk(edited_root):
    #    for f in files:
    #        images = os.listdir(subdir)
    #        if len(images) != 1:
    #            print('Error! "%s" should contain 1 image.', images)
    #        edited_index[
    #            os.path.basename(subdir)] = os.path.join(
    #            subdir, images[0])

    c = main_db.cursor()
    c.execute('SELECT COUNT(*) from RKMaster')
    (number_of_rows,) = c.fetchone()
    c.execute('SELECT * FROM RKMaster')

    bar = progressbar.ProgressBar(maxval=number_of_rows)

    for master in bar(iter(c.fetchone, None)):
        master_uuid = master['uuid']
        master_path = os.path.join(lib_dir, 'Masters', master['imagePath'])
        latitude = None
        longitude = None
        master_albums = set([])
        master_keywords = set([])
        master_rating = None

        # ignore image if it is in trash
        if master['isInTrash']:
            continue

        vc = main_db.cursor()
        vc.execute('SELECT * FROM RKVersion WHERE masterUuid=? and isInTrash=0', [master_uuid])
        edited_paths = []
        unadjusted_count = 0
        for version in iter(vc.fetchone, None):
            edited_path = []
            is_master = False

            if version['adjustmentUuid'] != 'UNADJUSTEDNONRAW':
                ac = proxy_db.cursor()
                ac.execute('SELECT * FROM RKModelResource WHERE resourceTag=?',
                           [version['adjustmentUuid']])
                for resource in iter(ac.fetchone, None):
                    if resource['attachedModelType'] == 2 and resource[
                            'resourceType'] == 4:
                        if len(edited_path) != 0:
                            pass
                            # print("Warning! Multiple valid edits!")

                        # Seems to not be a thing anymore with Apple Photos
                        # edited_path += [edited_index[resource['resourceUuid']]]
            else:
                unadjusted_count += 1
                is_master = True

            latitude = version['latitude']
            longitude = version['longitude']

            title = version['name']

            kc = main_db.cursor()
            kc.execute('SELECT * FROM RKAlbumVersion WHERE versionId=?',
                       [version['modelId']])
            albums = set([])
            for album_id in iter(kc.fetchone, None):
                alc = main_db.cursor()
                alc.execute('SELECT * FROM RKAlbum WHERE modelId=? and isInTrash=0',
                            [album_id['albumId']])
                r_albums = alc.fetchall()
                if len(r_albums) != 0:
                    if len(r_albums) != 1:
                        print(
                            "Warning! More than one album for ID %d" %
                            album_id['albumId'])
                    albums |= {r_albums[0]['uuid']}

            wc = main_db.cursor()
            wc.execute(
                'SELECT * FROM RKKeywordForVersion WHERE versionId=?', [version['modelId']])
            keywords = set([])
            for keyword_id in iter(wc.fetchone, None):
                klc = main_db.cursor()
                klc.execute('SELECT * FROM RKKeyword WHERE modelId=?',
                            [keyword_id['keywordId']])
                r_keyword = klc.fetchall()
                if len(r_keyword) != 0:
                    if len(r_keyword) != 1:
                        print(
                            "Warning! More than one keyword for ID %d" %
                            keyword_id['keywordId'])
                    keywords |= {r_keyword[0]['name']}

            rating = version['mainRating']

            # rating used just in old iPhoto. this converts a Favorite photo to
            # rating 5
            if version['isFavorite'] == 1:
                rating = 5

            if is_master:
                master_albums |= albums
                master_keywords |= keywords
                master_rating = rating
            else:
                for foo in edited_path:
                    iuuid = next_name(foo, namer)
                    edited_paths += [{'path': foo,
                                      'albums': list(albums),
                                      'keywords': list(keywords),
                                      'rating': rating,
                                      'uuid': iuuid,
                                      'in_library': True,
                                      'latitude': latitude,
                                      'longitude': longitude}]

        master_in_library = (unadjusted_count != 0)
        iuuid = next_name(master_path, namer)

        master_data = {
            'title': title,
            'uuid': iuuid,
            'path': master_path,
            'in_library': master_in_library,
            'albums': list(master_albums),
            'keywords': list(master_keywords),
            'rating': master_rating,
            'latitude': latitude,
            'longitude': longitude}
        # print(edited_paths)
        if unadjusted_count != 0 and unadjusted_count != 1:
            # print("Warning! %d unadjusted images!" % unadjusted_count)
            pass

        # create output_dir if not exists
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if os.path.isfile(master_path):
            # Export!
            base_export_path = os.path.join(output_dir, iuuid)
            # Copy the master
            shutil.copy2(
                master_path,
                os.path.join(
                   output_dir,
                   iuuid +
                   os.path.splitext(master_path)[1].lower()))
            # Write the data
            with open(os.path.join(output_dir, '%s.json' % iuuid), 'w') as log_file:
                print(
                    json.dumps(
                        dict(master_data, derived_from=None)),
                    file=log_file)
            # Copy the edits
            #edit_export_path = os.path.join(base_export_path, 'edited')
            for edit_info in edited_paths:
                shutil.copy2(
                    edit_info['path'],
                    os.path.join(
                        output_dir,
                        '%s%s' %
                        (edit_info['uuid'],
                         os.path.splitext(edit_info['path'])[1].lower())))

                with open(os.path.join(output_dir, '%s.json' % edit_info['uuid']), 'w') as log_file:
                    print(
                        json.dumps(
                            dict(edit_info, derived_from=iuuid)),
                        file=log_file)

    main_db.close()
    proxy_db.close()


# Usage: ./extract_photos.py <photo_library> <output_dir>
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
