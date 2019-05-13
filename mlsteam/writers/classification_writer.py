import os
import six
import click
import numpy as np
import tensorflow as tf
from PIL import Image


CLASSES_FILENAME = 'labels.txt'
IMAGE_PER_SHARD = 10000


def _int64_feature(value):
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def _float_feature(value):
    """Wrapper for inserting float features into Example proto."""
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _bytes_feature(value):
    if six.PY3 and isinstance(value, six.text_type):
        value = six.binary_type(value, encoding='utf-8')
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_array_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _convert_to_example(filename, image_buffer, height, width, label, text):
    """Build an Example proto for an example.
    """
    example = tf.train.Example(features=tf.train.Features(feature={
      'image/height': _int64_feature(height),
      'image/width': _int64_feature(width),
      'image/class/label': _int64_feature(label),
      'image/class/text': _bytes_feature(tf.compat.as_bytes(text)),
      'image/filename': _bytes_feature(tf.compat.as_bytes(filename)),
      'image/encoded': _bytes_feature(tf.compat.as_bytes(image_buffer))}))
    return example

def read_image(path):
    with tf.gfile.GFile(path, 'rb') as f:
        image = f.read()
    return image


class ClassificationWriter(object):
    def __init__(self, reader, output_dir, split='data'):
        self._reader = reader
        self._output_dir = output_dir
        self._split = split

    def save(self):
        tf.logging.info('Saving split "{}" in output_dir = {}'.format(
            self._split, self._output_dir))
        if not tf.gfile.Exists(self._output_dir):
            tf.gfile.MakeDirs(self._output_dir)

        self._reader.parse()
        # Save classes in text file for later use.
        labels = self._reader.labels()
        tf.logging.debug("labels: {}".format(labels))
        classes_file = os.path.join(self._output_dir, CLASSES_FILENAME)
        with open(classes_file, 'w') as outfile:
            outfile.write('\n'.join(labels) + '\n')

        tf.logging.debug('Found {} images.'.format(self._reader.total()))
        for label, value in self._reader.distribution():
            tf.logging.debug('Label {}: {}'.format(label, value))
        num_shards = self._reader.total() // IMAGE_PER_SHARD
        if (self._reader.total() % IMAGE_PER_SHARD) or num_shards == 0:
            num_shards += 1 # make this number or one
        tf.logging.debug("num_shards: {}".format(num_shards))
        filepaths, labels, texts = self._reader.get_shuffle_paths()
        assert len(filepaths) == len(labels)
        assert len(filepaths) == len(texts)

        # Break all images into batches with a [ranges[i][0], ranges[i][1]].
        spacing = np.linspace(0, len(filepaths), num_shards + 1).astype(np.int)
        ranges = []
        for i in range(len(spacing) - 1):
            ranges.append([spacing[i], spacing[i + 1]])
        shard = 0
        with click.progressbar(length=self._reader.total()) as bar:
            for enu, shard_range in enumerate(ranges):
                output_filename = '%s-%.5d-of-%.5d' % (self._split, enu, num_shards)
                output_file = os.path.join(self._output_dir, output_filename)
                writer = tf.python_io.TFRecordWriter(output_file)

                files_in_shard = np.arange(shard_range[0], shard_range[1], dtype=int)
                for i in files_in_shard:
                    filepath = filepaths[i]
                    label = labels[i]
                    text = texts[i]
                    image = read_image(filepath)

                    image_pil = Image.open(six.BytesIO(image))
                    width = image_pil.width
                    height = image_pil.height
                    example = _convert_to_example(filepath, image, height, width, label, text)
                    writer.write(example.SerializeToString())
                    bar.update(1)
                writer.close()
