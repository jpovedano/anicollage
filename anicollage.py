#!/usr/bin/env python

import argparse
import imageio
import logging
import numpy
import random
import os

from skimage import measure
from skimage.io import show, imshow, imsave, use_plugin
from skimage.color import label2rgb

def generate_slideshow(dir, outfile):
    files = sorted(os.listdir(dir))
    with open("{}".format(outfile),"w") as sf:
        for i,f in enumerate(files):
            sf.write("{}:{}".format(os.path.abspath(f),0.3))
            if (i != len(files) - 1):
                sf.write("crossfade:{}".format(0.3))



def segment_image(input_file, output_dir, show_images=False):
    # Open original image
    imgcolor = imageio.imread(input_file)
    # Open the grayscale version
    img = imageio.imread(input_file, as_gray=True)

    # Threshold
    mask = img > 10
    labeled, nlabels = measure.label(mask, return_num=True)
    labeled_color = label2rgb(labeled)
    print nlabels

    if show_images:
        imshow(labeled_color)
        imshow(imgcolor)
        show()

    labels = range(1,nlabels)
    random.shuffle(labels)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

        imsave('{d}/collage_{n:03d}.png'.format(d=output_dir, n=i), masked)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Input image")
    parser.add_argument('outdir', help="Output directory")
    #TODO: Generate slideshow

    args = parser.parse_args()

    use_plugin('gtk')
    use_plugin('pil')

    segment_image(args.input, args.outdir)
    generate_slideshow(args.outdir, '{d}/slideshow.txt'.format(d=args.outdir))

if __name__ == '__main__':
    main()