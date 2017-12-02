#!/usr/bin/env python

import argparse
import requests
import yaml

from xml.etree import ElementTree


ALBUM_LIST_URL = "https://api.flickr.com/services/rest/?method=flickr.photosets.getList&api_key={api_key}&user_id={user_id}"
PHOTO_LIST_URL = "https://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key={api_key}&user_id={user_id}&photoset_id={album_id}"


def get_album_ids(api_key, user_id):
    
    url = ALBUM_LIST_URL.format(api_key=api_key, user_id=user_id)
    album_list_response = requests.get(url)
    
    parsed_xml_root = ElementTree.fromstring(album_list_response.content)
    try:
        photosets = parsed_xml_root.getchildren()[0]
    except IndexError as e:
        print("Could not find photosets in xml returned from flickr api")
        return []

    return [photoset.attrib['id'] for photoset in photosets.getchildren()]

def get_photo_configuration(api_key, user_id, album_id, thumb_ordering_from_flickr):
    
    url = PHOTO_LIST_URL.format(api_key=api_key, user_id=user_id, album_id=album_id)
    photo_list_response = requests.get(url)

    parsed_xml_root = ElementTree.fromstring(photo_list_response.content)
    photoset_root = parsed_xml_root.getchildren()[0]
    photoset_title = photoset_root.attrib['title']
    photoset_cover_id = photoset_root.attrib['primary']
    photoset_cover_name = None

    photo_elements = photoset_root.getchildren()
    ordering_filenames = []

    for photo_element in photo_elements:
        photo_filename = "%s.jpg" % photo_element.attrib['title']
        if photo_element.attrib['id'] == photoset_cover_id:
            photoset_cover_name = photo_filename
        ordering_filenames.append(photo_filename)

    thumbnails = None
    if thumb_ordering_from_flickr:
        num_usable_thumbnails = min(5, len(ordering_filenames))
        thumbnails = ordering_filenames[0:num_usable_thumbnails]
    
    return {
        'title': photoset_title,
        'cover': photoset_cover_name,
        'thumbnails': thumbnails,
        'ordering': ordering_filenames
    }


def main():

    parser = argparse.ArgumentParser(
        description='Build configuration files for 50mm web gallery by '
                    'exporting from the flickr API')
    parser.add_argument('api_key', metavar='Flickr_API_Key', type=str,
                        help='Your Flickr API Key, obtained from Flickr.')
    parser.add_argument('user_id', metavar='Flickr_User_ID',
                        help='The User ID on flickr which owns the Photosets '
                        'you are trying to export, this ID is usually in your '
                        'URLs')
    parser.add_argument('--do-thumbnails',
                        dest='thumbnails_from_flickr_order',
                        action='store_true',
                        help='Whether or not we generate a "thumbnails" '
                        'section for your configuration, ommitting this makes '
                        '50mm take bucket ordering by default for thumbnails')

    args = parser.parse_args()

    api_key = args.api_key
    user_id = args.user_id
    thumbnails_from_flickr_order = args.thumbnails_from_flickr_order
    
    print("Getting album IDs from flickr")
    album_ids = get_album_ids(api_key, user_id)
    print("Got %s albums: %s" % (len(album_ids), album_ids))

    for album_id in album_ids:
        print("Processing album %s" % album_id)
        album_config = get_photo_configuration(api_key, user_id, album_id, thumbnails_from_flickr_order)

        print("Extracted configuration for %s, name: %s" % (album_id, album_config['title']))
        if not thumbnails_from_flickr_order:
            album_config.pop('thumbnails')

        filename = "%s.yaml" % album_config.pop('title')

        with open(filename, 'w') as writeyaml:
            yaml.dump(album_config, writeyaml)
        print("Exported album config for %s to %s" % (album_id, filename))
        print("\n")
