from .classification_writer import ClassificationWriter # noqa
from luminoth.tools.dataset.writers.object_detection_writer import ObjectDetectionWriter
#from .object_detection_writer import ObjectDetectionWriter  # noqa

WRITERS = {
    'classification': ClassificationWriter,
    'coco': ObjectDetectionWriter,
    'csv': ObjectDetectionWriter,
    'flat': ObjectDetectionWriter,
    'imagenet': ObjectDetectionWriter,
    'openimages': ObjectDetectionWriter,
    'pascal': ObjectDetectionWriter,
    'taggerine': ObjectDetectionWriter,
    'kitti': ObjectDetectionWriter,
}


def get_writer(writer):
    writer = writer.lower()
    if writer not in WRITERS:
        raise ValueError('"{}" is not a valid writer'.format(writer))
    return WRITERS[writer]
