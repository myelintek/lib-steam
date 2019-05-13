import os
import random

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.ppm', '.pgm')

class ClassiReader(object):
    def __init__(self, data_dir, split, **kwargs):
        super(ClassiReader, self).__init__(**kwargs)
        self._split = split
        self._data_dir = data_dir
        self._distribution = {}
        self._file_paths = []
        self._file_texts = []
        self._labelid = {} # {'dog':0,'cat':1,'pig':2}

    def parse(self):
        subdirs = []
        if os.path.exists(self._data_dir) and os.path.isdir(self._data_dir):
            for filename in os.listdir(self._data_dir):
                subdir = os.path.join(self._data_dir, filename)
                if os.path.isdir(subdir):
                    subdirs.append(subdir)
        else:
            raise InvalidDataDirectory('folder does not exist')
        subdirs.sort()

        if len(subdirs) < 2:
            raise InvalidDataDirectory('folder must contain at least two subdirectories')

        label_index = 0
        for subdir in subdirs:
            # Use the directory name as the label
            label_name = subdir
            label_name = os.path.basename(label_name)
            if label_name.endswith('/'):
                # Remove trailing slash
                label_name = label_name[0:-1]
            if label_name not in self._distribution:
                self._distribution[label_name] = 0
            if label_name not in self._labelid:
                self._labelid[label_name] = label_index

            # Read all images in the subdir/label_name folder
            for dirpath, _, filenames in os.walk(os.path.join(self._data_dir, subdir), followlinks=True):
                for filename in filenames:
                    if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                        self._file_paths.append('%s' % (os.path.join(self._data_dir, subdir, dirpath, filename)))
                        self._file_texts.append(label_name)
                        self._distribution[label_name] += 1
            label_index += 1

    def labels(self):
        return list(self._distribution.keys())

    def distribution(self):
        return self._distribution.items()

    def total(self):
        return len(self._file_paths)

    def get_shuffle_paths(self):
        shuffled_index = list(range(len(self._file_paths)))
        random.seed(12345)
        random.shuffle(shuffled_index)
        filepaths = [self._file_paths[i] for i in shuffled_index]
        texts = [self._file_texts[i] for i in shuffled_index]
        labels = [self._labelid[text] for text in texts]
        return filepaths, labels, texts
