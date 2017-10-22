import random
import matplotlib.pylab as plab
import numpy as np
from typing import Callable, List, Tuple, Dict, Iterator

import os

Filequeue = Dict[str, List[Tuple[str, str]]]


class ImageFeeder:
    def __init__(
            self,
            path_to_files: str,
            class_extractor: Callable[[str], str],
            *,
            split: List[int] = None,
            filter_datatype: str = '.png',
            shuffle: bool = True,
            cycle: bool = True,
            use_one_hot: bool = True,
            flatten_input: bool = True,
            stack_direction: str = 'column'
    ) -> None:

        self.path_to_files = path_to_files
        self.class_extractor = class_extractor
        self.shuffle = shuffle
        self.cycle = cycle
        self.filter_datatype = filter_datatype
        self.use_one_hot = use_one_hot

        self.stack_direction = stack_direction
        assert self.stack_direction in ['column', 'row']
        self.flatten_input = flatten_input

        self.split = split if split is not None else [0.7, 0.15, 0.15]
        assert len(self.split) == 3 and sum(self.split) == 1.0

        self.file_queue: Filequeue = self._build_file_queue()
        self.classes = self._build_classlist()

        self._train_iter, self._test_iter, self._validation_iter = (None, None, None)
        self.refresh_iterators()

    def refresh_iterators(self) -> None:
        self._train_iter = self._iterate_over('train')
        self._test_iter = self._iterate_over('test')
        self._validation_iter = self._iterate_over('validation')

    def _iterate_over(self, dist: str) -> Iterator[Tuple[str, str]]:
        assert dist in ['train', 'test', 'validation']
        queue = self.file_queue[dist]
        if self.shuffle:
            # don't use random.shuffle to avoid shuffline the filequeue in place
            # treating the filequeue as constant makes testing/validating the code easier
            queue = random.sample(queue, len(queue))

        for file_and_label in queue:
            yield file_and_label

        # recurse to handle iterating over multiple epochs
        # will also cause each epoch to have a distinct shuffle
        if self.cycle:
            yield from self._iterate_over(dist)

    def get_batch(self, dist: str, amount: int) -> Tuple[np.array, np.array]:
        assert dist in ['train', 'test', 'validation']
        iterator = getattr(self, f'_{dist}_iter')

        inputs = []
        labels = []

        for i, (file, label) in enumerate(iterator):
            inputs.append(self._load_image(file))
            labels.append(self._load_label(label))

            if i + 1 == amount:
                break

        # TODO should probably use np.stack here
        stack_func = np.hstack if self.stack_direction == 'column' else np.vstack
        return stack_func(inputs), stack_func(labels)

    def _load_image(self, file: str) -> np.array:
        input_image = plab.imread(file)
        if self.flatten_input:
            # look at the stack direction to determine flattening direction
            vector_size = np.multiply.reduce(input_image.shape)
            new_shape = [vector_size, 1] if self.stack_direction == 'column' else [1, vector_size]
            input_image = input_image.reshape(new_shape)
        return input_image

    def _load_label(self, label: str) -> np.array:
        if self.use_one_hot:
            # look at the stack direction to determine flattening direction
            one_hot = self.label_one_hot(label)
            vector_size = len(self.classes)
            new_shape = [vector_size, 1] if self.stack_direction == 'column' else [1, vector_size]
            label = np.array(one_hot).reshape(new_shape)
        return label

    def get_text_label(self, one_hot: List[int]) -> str:
        idx = one_hot.index(max(one_hot))
        return self.classes[idx]

    def label_one_hot(self, label: str) -> List[int]:
        template = [0 for _ in self.classes]
        template[self.classes.index(label)] = 1
        return template

    def _build_file_queue(self) -> Filequeue:
        files = [os.path.join(self.path_to_files, f) for f in os.listdir(self.path_to_files) if
                 f.endswith(self.filter_datatype)]
        labels = [self.class_extractor(f) for f in files]
        all_examples = list(zip(files, labels))
        size = len(all_examples)

        train_index = int(self.split[0] * size)
        test_index = int((self.split[0] + self.split[1]) * size)
        queue = {
            'train': all_examples[:train_index],
            'test': all_examples[train_index:test_index],
            'validation': all_examples[test_index:]
        }
        return queue

    def _build_classlist(self) -> List[str]:
        all_files = self.file_queue['train'] + self.file_queue['test'] + self.file_queue['validation']
        return list(set(x[1] for x in all_files))
