#! /usr/bin/env python3

import sys, os, sqlite3, hashlib, json

lib_dir = sys.argv[1]
output_dir = sys.argv[2]

db_path = os.path.join(lib_dir, 'database')
main_db_path = os.path.join(db_path, 'Library.apdb')
proxy_db_path = os.path.join(db_path, 'ImageProxies.apdb')
edited_root = os.path.join(lib_dir, 'resources', 'modelresources')
edited_index = {}
for subdir, dirs, files in os.walk(edited_root):
    for f in files:
        images = os.listdir(subdir)
        if len(images) != 1:
            print('Error! "%s" should contain 1 image.', images)
        edited_index[os.path.basename(subdir)] = os.path.join(subdir, images[0])
# print(edited_index)
# print(main_db_path)
# print(proxy_db_path)

main_db = sqlite3.connect(main_db_path)
main_db.row_factory = sqlite3.Row
proxy_db = sqlite3.connect(proxy_db_path)
proxy_db.row_factory = sqlite3.Row

c = main_db.cursor();
c.execute('SELECT * FROM RKMaster')
uuids = {}
euuids = {}
for master in iter(c.fetchone, None):
    master_uuid = master['uuid']
    master_path = os.path.join(lib_dir, 'Masters', master['imagePath'])
    master_albums = set([])
    master_keywords = set([])
    master_rating = None
    vc = main_db.cursor();
    vc.execute('SELECT * FROM RKVersion WHERE masterUuid=?', [master_uuid])
    edited_paths = []
    unadjusted_count = 0
    for version in iter(vc.fetchone, None):
        edited_path = []
        is_master = False
        if version['adjustmentUuid'] != 'UNADJUSTEDNONRAW':
            ac = proxy_db.cursor();
            ac.execute('SELECT * FROM RKModelResource WHERE resourceTag=?', [version['adjustmentUuid']])
            for resource in iter(ac.fetchone, None):
                if resource['attachedModelType'] == 2 and resource['resourceType'] == 4:
                    if len(edited_path) != 0:
                        print("Warning! Multiple valid edits!")
                    edited_path += [edited_index[resource['resourceUuid']]]
        else:
            unadjusted_count += 1
            is_master = True

        kc = main_db.cursor()
        kc.execute('SELECT * FROM RKAlbumVersion WHERE versionId=?', [version['modelId']])
        albums = set([])
        for album_id in iter(kc.fetchone, None):
            alc = main_db.cursor()
            alc.execute('SELECT * FROM RKAlbum WHERE modelId=?', [album_id['albumId']])
            r_albums = alc.fetchall()
            if len(r_albums) != 0:
                if len(r_albums) != 1:
                    print("Warning! More than one album for ID %d" % album_id['albumId'])
                albums |= set([r_albums[0]['name']])

        wc = main_db.cursor()
        wc.execute('SELECT * FROM RKKeywordForVersion WHERE versionId=?', [version['modelId']])
        keywords = set([])
        for keyword_id in iter(kc.fetchone, None):
            klc = main_db.cursor()
            klc.execute('SELECT * FROM RKKeyword WHERE modelId=?', [keyword_id['keywordId']])
            r_keyword = klc.fetchall()
            if len(r_keyword) != 0:
                if len(r_keyword) != 1:
                    print("Warning! More than one keyword for ID %d" % keyword_id['keywordId'])
                keywords |= set([r_keyword[0]['name']])

        rating = version['mainRating']
        if is_master:
            master_albums |= albums
            master_keywords |= keywords
            master_rating = rating
        else:
            for foo in edited_path:
                euuid = hashlib.md5(open(foo,'rb').read()).hexdigest()
                if euuid not in euuids:
                    euuids[euuid] = 0
                euuids[euuid] += 1
                edited_paths += [{'path': foo, 'albums': list(albums), 'keywords': list(keywords), 'rating': rating, 'uuid': 'e-%s%03d' % (euuid, euuids[euuid]-1)}]

    master_in_library = (unadjusted_count != 0)
    uuid = hashlib.md5(open(master_path,'rb').read()).hexdigest()
    if uuid in uuids:
        print("Duplicate photo: %s, %s" % (uuid, master_path))
    else:
        uuids[uuid] = 0
    uuids[uuid] += 1
    extended_uuid = '%s%03d' % (uuid, uuids[uuid]-1)

    photo_data = {'extended_uuid': extended_uuid, 'path': master_path, 'master_in_library': master_in_library, 'albums': list(master_albums), 'keywords': list(master_keywords), 'rating': master_rating, 'edits': edited_paths}
    json_data = json.dumps(photo_data)
    print(json_data)
    if unadjusted_count != 0 and unadjusted_count != 1:
        print("Warning! %d unadjusted images!" % unadjusted_count)

    # Export!
    base_export_path = os.path.join(output_dir, extended_uuid)
    # Hard link the master
    os.link(master_path, os.path.join(output_dir, extended_uuid + os.path.splitext(master_path)[1]))
    # Write the data
    with open(os.path.join(output_dir, '%s.json' % extended_uuid), 'w') as log_file:
        print(json_data, file=log_file)
    # Hard link the edits
    edit_export_path = os.path.join(base_export_path, 'edited')
    for edit_info in edited_paths:
            os.link(edit_info['path'], os.path.join(output_dir, '%s-%s%s'% (extended_uuid, edit_info['uuid'], os.path.splitext(edit_info['path'])[1])))

    print("****************")
