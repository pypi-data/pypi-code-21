
# coding: utf-8

# In[ ]:


from os.path import exists, join, basename
from os import makedirs, remove
from six.moves import urllib
import tarfile
from torchvision.transforms import ToTensor
import sys
from utils.log import warning, error

class get_dataset():
    def extract_files(file_path, dest):
        if filename.endswith(".tar*"): return extract_tar(file_path, dest)
        elif filename.endswith(".zip"): error("Zip extraction not yet implemented")
        else: error(f"Extraction method for {filename} not known")

    def extract_tar(file_path, dest, remove_filepath = True):
        print("Extracting data")
        with tarfile.open(file_path) as tar:
            for item in tar:
                tar.extract(item, dest)
        if remove_filepath:
            remove(file_path)

    def download_and_extract_dataset(url, dest = "datasets", dataset_name = basename(url)):
        output_image_dir = join(dest, dataset_name, "images")

        if not exists(output_image_dir):
            makedirs(dest)
            print(f"Downloading url: {url}")

            data = urllib.request.urlopen(url)

            file_path = join(dest, basename(url))
            with open(file_path, 'wb') as f:
                f.write(data.read())

            extract_files(file_path, dest)

        return output_image_dir

