import asyncio
import progressbar
from os import walk, makedirs
from kraem.compress import compress
from kraem.gcs import upload

destination_files = []


# Prepend sub folder name to files
def prepend_folder_name(name, files):
    images = []

    for file in files:
        images.append('%s/%s' % (name, file))

    return images


# Get all images from source directory
def get_images_from_dir(source):
    images = []

    for (dirpath, dirnames, filenames) in walk(source):
        images.extend(prepend_folder_name(dirpath, filenames))

    return images


# A very haxxy function which creates folders
def create_directories(dest):
    destination = dest.split('/')

    destination.pop()

    folder = '/'.join(destination)

    makedirs(folder, exist_ok=True)


def set_destination_files(destination):
    destination_files.append(destination)


def get_destination_files():
    return destination_files


# Compress all images
def compressor(args):
    # consider https://docs.python.org/3/library/concurrent.futures.html
    loop = asyncio.get_event_loop()

    files = get_images_from_dir(args.source)

    bar = progressbar.ProgressBar(max_value=len(files))

    for idx, file in enumerate(files):
        # Not the best solution. Should reconsider this approach
        dest = file.replace('%s/' % args.source, '%s/' % args.destination)

        create_directories(dest)

        loop.run_until_complete(
            compress(
                file,
                dest,
                args.quality
            )
        )

        bar.update(idx + 1)

        set_destination_files(dest)

    return loop


# This is the applications entry point
def run(args):
    print(' Compressing images...')
    compressor(args).close()

    if args.gcs:
        print('\n Uploading images to Google Cloud Storage...')

        upload(args.gcs, get_destination_files())

    print('\n Finished :)')
