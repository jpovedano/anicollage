#!/usr/bin/env python

import logging
import imageio
import random
import numpy
from skimage import measure
from skimage.io import show, imshow, imsave, use_plugin
from skimage.color import label2rgb
import os

def generate_slideshow(dir, outfile):
    files = sorted(os.listdir(dir))
    with open("{}".format(outfile),"w") as sf:
        for i,f in enumerate(files):
            sf.write("{}:{}".format(os.path.abspath(f),0.3))
            if (i != len(files) - 1):
                sf.write("crossfade:{}".format(0.3))



def segment_image(input_file):
    # Open original image
    imgcolor = imageio.imread(input_file)
    # Open the grayscale version
    img = imageio.imread(input_file, as_gray=True)

    # Threshold
    mask = img > 10
    labeled, nlabels = measure.label(mask, return_num=True)
    labeled_color = label2rgb(labeled)
    print nlabels
    imshow(labeled_color)

    labels = range(1,nlabels)
    random.shuffle(labels)

    for i in range(1,nlabels):
        logging.info("Processing frame {i}".format(i=i))
        threshf = lambda x: x in labels[0:i]
        vthres = numpy.vectorize(threshf)
        labeled_thres = vthres(labeled)

        # Now we create a image with the alement masked

        # tuples are not mutable, we need an additional channel for alpha
        shape = list(imgcolor.shape)
        shape[2] += 1
        masked = numpy.zeros(tuple(shape), dtype=numpy.uint8)

        # Apply the mask to the three components
        masked[:,:,0] = imgcolor[:,:,0] * labeled_thres
        masked[:,:,1] = imgcolor[:,:,1] * labeled_thres
        masked[:,:,2] = imgcolor[:,:,2] * labeled_thres
        masked[:,:,3] = labeled_thres * 255

        imsave('collage/collage_{n:03d}.png'.format(n=i), masked)
    imshow(imgcolor)
    show()


if __name__ == '__main__':
    use_plugin('gtk')
    use_plugin('pil')
    segment_image('E-0410.JPG')
    generate_slideshow('collage', 'collage/slideshow.txt')