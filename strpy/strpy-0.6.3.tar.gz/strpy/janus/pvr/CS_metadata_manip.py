""" methods for parsing and manipulating CS0/CS1 metadata """
import csv
import os.path
import glob


def create_CS_subject_all_sightings_map(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    sighting_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/*.csv')
        sids  = []
        files = []
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    sighting_id = int(row['SIGHTING_ID'])
                    sids.append(sighting_id)
                    files.append(img_name)
        sighting_map[subject_dir] = {'files':files, 'sightings':sids}
    return sighting_map

def create_CS_subject_sighting_map(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    sighting_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/*.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    sighting_id = int(row['SIGHTING_ID'])
                    media_id = int(row['MEDIA_ID'])
                    sighting_map[sighting_id] = {'file':img_name, 'subject':subject_dir, 'media_id':media_id}
    return sighting_map

def create_CS_gallery_subject_sighting_map(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    sighting_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/gallery.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    mid = int(row['MEDIA_ID'])
                    tid = int(row['TEMPLATE_ID'])
                    sighting_id = int(row['SIGHTING_ID'])
                    if sighting_id in sighting_map and tid not in sighting_map[sighting_id]['template']:
                        sighting_map[sighting_id]['template'].append(tid)
                    else:
                        sighting_map[sighting_id] = {'file':img_name, 'subject':subject_dir, 'template':[tid,],'media':mid}
    return sighting_map

def CS_probes_as_templates(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    template_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/probe.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    mid = int(row['MEDIA_ID'])
                    tid = int(row['TEMPLATE_ID'])
                    sid = int(row['SIGHTING_ID'])
                    if tid not in template_map:
                        template_map[tid] = {'subject':subject_dir, 'media':dict([])}
                        template_map[tid]['media'][mid] = [sid,]
                    elif mid not in template_map[tid]['media']:
                        template_map[tid]['media'][mid] = [sid,]
                    else:
                        template_map[tid]['media'][mid].append(sid)

    return template_map


def CS_gallery_as_media(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    media_map = {}
    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/gallery.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    mid = int(row['MEDIA_ID'])
                    tid = int(row['TEMPLATE_ID'])
                    sid = int(row['SIGHTING_ID'])
                    if mid not in media_map:
                        media_map[mid] = {'subject':subject_dir, 'sightings':[sid,]}
                    else:
                        media_map[mid]['sightings'].append(sid)
    return media_map


def create_CS_probe_subject_sighting_map(CS_dir):
    """ return dictionary {sighting_id: {'file':filename, 'subject':subject_name}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    sighting_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/probe.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    mid = int(row['MEDIA_ID'])
                    tid = int(row['TEMPLATE_ID'])
                    sighting_id = int(row['SIGHTING_ID'])
                    if sighting_id in sighting_map and tid not in sighting_map[sighting_id]['template']:
                        sighting_map[sighting_id]['template'].append(tid)
                    else:
                        sighting_map[sighting_id] = {'file':img_name, 'subject':subject_dir, 'template':[tid,],'media':mid}
    return sighting_map


def create_CS_subject_id_name_map(CS_dir):
    """ return dictionary {subject_id: 'subject name'} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    name_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/*.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    subject_id = int(row['SUBJECT_ID'])
                    name_map[subject_id] = os.path.basename(subject_dir)
                    # all sightings should have the same subject id, no need to process them all
                    break
    return name_map


def create_CS_template_subject_id_map(CS_dir):
    """ return dictionary {template_id: subject_id} """
    template_dict = {}

    csv_files = glob.glob(CS_dir + '/protocol/*.csv')
    for csv_file in csv_files:
        with open(csv_file, 'rb') as fd:
            reader = csv.DictReader(fd)
            for row in reader:
                subject_id = int(row['SUBJECT_ID'])
                template_id = int(row['TEMPLATE_ID'])
                if template_id in template_dict:
                    # if we've already seen this template id, make sure no conflict (shouldn't happen)
                    if subject_id != template_dict[template_id]:
                        raise Exception('Inconsistent data for template id ' + str(template_id))
                template_dict[template_id] = subject_id
    return template_dict

def create_CS_template_subject_id_map_split(csv_files, CS_dir=None):
    """ return dictionary {template_id: subject_id} """
    template_dict = {}

    #csv_files = glob.glob(CS_dir + '/protocol/*.csv')
    for csv_file in csv_files:
        with open(csv_file, 'rb') as fd:
            reader = csv.DictReader(fd)
            for row in reader:
                subject_id = int(row['SUBJECT_ID'])
                template_id = int(row['TEMPLATE_ID'])
                if template_id in template_dict:
                    # if we've already seen this template id, make sure no conflict (shouldn't happen)
                    if subject_id != template_dict[template_id]:
                        raise Exception('Inconsistent data for template id ' + str(template_id))
                template_dict[template_id] = subject_id
    return template_dict


def create_CS_template_sighting_id_map(csv_files):
    """ return dictionary {template_id: [sighting_ids]} """
    template_dict = {}

    if isinstance(csv_files,str):
        csv_files = [csv_files,]

    for csv_file in csv_files:
        with open(csv_file, 'rb') as fd:
            reader = csv.DictReader(fd)
            for row in reader:
                template_id = int(row['TEMPLATE_ID'])
                sighting_id = int(row['SIGHTING_ID'])
                if template_id in template_dict:
                    # we've already seen this template id, add this sighting to the list
                    template_dict[template_id].append(sighting_id)
                else:
                    # new template id
                    template_dict[template_id] = [sighting_id,]
    return template_dict


def create_CS_media_map(CS_dir):
    """ return dictionary {media_id: {sightings:{sighting_id: {'file':filename, 'subject':subject}}}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    media_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/*.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    sighting_id = int(row['SIGHTING_ID'])
                    media_id = int(row['MEDIA_ID'])
                    sighting_entry = {'file':img_name}

                    if media_id not in media_map:
                        # previously unseen media - create a new entry with a single sighting
                        media_map[media_id] = {'sightings':dict(), 'subject':subject_dir}

                    media_map[media_id]['sightings'][sighting_id] = sighting_entry
    return media_map

def create_CS_template_map(CS_dir):
    """ return dictionary {media_id: {sightings:{sighting_id: {'file':filename, 'subject':subject}}}} """
    subjects_base_dir = CS_dir + '/subjects'
    subject_dirs = os.listdir(subjects_base_dir)
    subject_dirs = [d for d in subject_dirs if os.path.isdir(subjects_base_dir + '/' + d)]

    template_map = {}

    for subject_dir in subject_dirs:
        csv_files = glob.glob(subjects_base_dir + '/' + subject_dir + '/*.csv')
        for csv_file in csv_files:
            with open(csv_file, 'rb') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    img_name = row['FILE']
                    sighting_id = int(row['SIGHTING_ID'])
                    template_id = int(row['TEMPLATE_ID'])
                    sighting_entry = {'file':img_name}

                    if template_id not in template_map:
                        # previously unseen media - create a new entry with a single sighting
                        template_map[template_id] = {'sightings':dict(), 'subject':subject_dir}

                    template_map[template_id]['sightings'][sighting_id] = sighting_entry
    return template_map
