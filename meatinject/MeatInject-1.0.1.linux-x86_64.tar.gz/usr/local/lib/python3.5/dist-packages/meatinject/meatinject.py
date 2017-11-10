# meatinject.py 
# Tool that can replace all files in a directory with meatspin
# author: embarassed author
# Requirements:
#  pip install wand

from wand.image import Image
from wand.display import display
import requests
import shutil
import argparse
import os
listdir = os.listdir
MEATSPIN = 'meatspin.demo' # path to meatspin.gif

def main():

    parser = argparse.ArgumentParser(
        description='Image Meatspin injector')
    parser.add_argument('-f',
        dest='path',
        help="Folder containing images")
    parser.add_argument('-g',
        dest='gif',
        action="store_true",
        help='Only inject onto gifs to be more subtle')
    parser.add_argument('-d',
        dest='debug',
        action='store_true',
        help="Debug output")
    args = parser.parse_args()
    path = args.path
    if not path:
        path = '.'
    file_check(path)
    if args.gif:
        image_extensions = [".gif"]
    else:
        image_extensions = [".gif", ".png", ".jpg"]
    files = [x for x in listdir(path) if str(x[-4:]) in image_extensions]
    counter = 0
    for file in files:
      file = path + '/' + file
      print("'Adjusting' file: %s" % file)
      with Image(filename=file) as img:
        with Image(filename=MEATSPIN) as meat:
            meat.resize(img.size[0], img.size[1])
            meat.sequence.insert(0,img)
            meat.sequence.insert(len(meat.sequence), img)
            if args.debug:
                meat.save(filename="Balls.gif")
            else:
                meat.save(filename=file)
            counter += 1
    print("Injected meatspin into %s images" % counter)

def file_check(path):
    # check if meatspin exists
    if os.path.exists(MEATSPIN):
        print("Meatspin.gif found! Continuing on")
    else:
        print("Can't find the meatspin...")
        answer = raw_input("Do you want me to download meatspin for you? Y/N")
        if answer == '' or answer.lower() == "y":
            r = requests.get('http://vignette3.wikia.nocookie.net/t101medialifestudyguide/images/3/3d/Meatspin.gif/revision/latest?cb=20100304041345', stream=True)
            with open(MEATSPIN, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    main()
