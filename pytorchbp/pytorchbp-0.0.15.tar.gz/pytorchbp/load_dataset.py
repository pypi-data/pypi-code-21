
# coding: utf-8

# In[ ]:


import torch.utils.data as data

from os import listdir
from os.path import join
from PIL import Image
from . import logger
warning = logger.warning
error = logger.error

class load_dataset():
    def is_image_file(filename):
        return(any(filename.endswith(extension) for extension in [".png", ".jpg", ".jpeg"]))

    def load_img(filepath):
        img = Image.open(filepath).convert('YCbCr')
        warning("Might be super-resolution specific. Check here if images are loading incorrectly.")
        y, _, _ = img.split()
        return y

    class DatasetFromFolder(data.Dataset):
        def __init__(self, image_dir, input_transform = None, target_transform = None):
            super(DatasetFromFolder, self).__init__()
            self.image_filenames = [join(image_dir, x) for x in listdir(image_dir) if is_image_file(x)]

            self.input_transform = input_transform
            self.target_transform = target_transform

        def __getitem__(self, index):
            input = load_img(self.image_filenames[index])
            target = input.copy()
            if self.input_transform:
                input = self.input_transform(input)
            if self.target_transform:
                target = self.target_transform(target)

            return input, target

        def __len__(self):
            return len(self.image_filenames)

    def input_transform(transforms = default_transforms):
        return Compose(transforms)

    def target_transform(transforms = default_transforms):
        return Compose(transforms)

    def get_train_set(root_dir):
        train_dir = join(root_dir, "train")

        return DatasetFromFolder(train_dir,
                                input_transform = input_transform(),
                                target_transform = target_transform())

    def get_val_set(root_dir):
        val_dir = join(root_dir, "val")

        return DatasetFromFolder(val_dir,
                                input_transform = input_transform(),
                                target_transform = target_transform())

    def get_test_set(root_dir):
        test_dir = join(root_dir, "test")

        return DatasetFromFolder(test_dir,
                                input_transform = input_transform(),
                                target_transform = target_transform())

    def get_split_data(root_dir):
        return get_train_set(root_dir), get_val_set(root_dir), get_test_set(root_dir)

    def get_split_data_loaders(root_dir, batch_size =  None):
        import multiprocessing
        pool = multiprocessing.Pool()
        warning("Using multiprocessing.Pool(). Might not close correctly.")

        if batch_size is None:
            warning("Batch size not specified. Using default of 64.")
            batch_size = 64

        train_data_loader = DataLoader(dataset = get_train_set(root_dir), num_workers = pool._processes, 
                                          batch_size = batch_size, shuffle = True)

        val_data_loader = DataLoader(dataset = get_val_set(root_dir), num_workers = pool._processes, 
                                          batch_size = batch_size, shuffle = True)

        test_data_loader = DataLoader(dataset = get_test_set(root_dir), num_workers = pool._processes, 
                                          batch_size = batch_size, shuffle = True)

        return train_data_loader, val_data_loader, test_data_loader

