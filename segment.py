#!/usr/bin/env python

import imageio
import random
import numpy
from skimage import measure
from skimage.io import show, imshow, imsave, use_plugin
from skimage.color import label2rgb


def segment_image(input_file):
    img = imageio.imread(input_file, as_gray=True)

    mask = img > 10
    labeled, nlabels = measure.label(mask, return_num=True)
    labeled_color = label2rgb(labeled)
    print nlabels
    imshow(labeled_color)

    labels = range(1,nlabels)
    random.shuffle(labels)

    for i in range(1,nlabels):
        threshf = lambda x: x in labels[0:i]
        vthres = numpy.vectorize(threshf)
        labeled_thres = vthres(labeled)
        #labeled_color_thres = label2rgb(labeled_thres,)
        #imshow(labeled_thres)
        imsave('collage/collage_{n:03d}.png'.format(n=i),labeled_thres * 255)

    show()


if __name__ == '__main__':
    use_plugin('gtk')
    use_plugin('pil')
    segment_image('E-0410.JPG')