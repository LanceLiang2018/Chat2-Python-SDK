import os
from skimage import io, filters, exposure
from skimage.morphology import disk
import numpy as np
from PIL import Image


def if_in(key: str, data: dict, default=False):
    if key in data:
        return data[key]
    return default


def image_process(image, save_name=None,
                  black_white=False,
                  intensity=False,
                  hist=False,
                  median=False,
                  sobel=False,
                  high_enhance=False,
                  trans=False,
                  option=None):
    # im = io.imread(image, as_gray=True)
    im = image

    if option is not None:
        black_white = if_in('black_white', option)
        intensity = if_in('intensity', option)
        hist = if_in('hist', option)
        median = if_in('median', option)
        sobel = if_in('sobel', option)
        trans = if_in('trans', option)

    if hist is True:
        im = exposure.equalize_hist(im)

    if high_enhance is True:
        im = filters.rank.enhance_contrast(im, disk(5))
        im = 1 - im

    if median is True:
        im = filters.median(im, disk(5))
        im = 1 - im

    if sobel is True:
        im = filters.sobel(im)
        im = 1 - im

    if intensity is True:
        im = exposure.rescale_intensity(im)

    if black_white is True:
        thresh = filters.threshold_otsu(im)
        im = (im >= thresh) * 1.0

    if trans is True:
        im = 1 - im

    im = im * 255
    im = np.array(im, dtype=np.uint8)
    # io.imsave(save_name, im)
    # Image.fromarray(im).convert("RGB").save(save_name + '.jpg')
    return im


if __name__ == '__main__':
    for file in os.listdir('imgs/'):
        print("TEST:", file)
        # image_process('imgs/%s' % file, save_name='results/%s' % file,
        #               intensity=True, median=False, sobel=False,
        #               high_enhance=False, black_white=True, trans=False)
        im = io.imread('imgs/%s' % file, as_gray=True)
        im = image_process(im, option={'black_white': True})
        io.imsave('results/%s.jpg' % file, im)