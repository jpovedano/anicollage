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


def generate_slideshow(dir, outfile, delay=0.25):
    files = sorted(os.listdir(dir))
    with open("{}".format(outfile), "w") as sf:
        for i, f in enumerate(files):
            filename = os.path.abspath(os.path.join(dir, f))
            sf.write("{}:{}\n".format(filename, delay))
            if (i != len(files) - 1):
                sf.write("crossfade:{}\n".format(delay))


# Return a list o labels in certain order
def sort_regions(regions, costmap=None):
    center = numpy.subtract(regions[-1].centroid, regions[0].centroid)

    def reg_dist_score(a, b):
        return numpy.linalg.norm(numpy.subtract(b, a))

    return [r.label for r in sorted(regions, key=lambda x: reg_dist_score(x.centroid[1], center[0]))]

# This function uses the centroid position to calculate the weigth.
# This does not work correctly for excentric regions


def sort_colormap_centroid(regions, costmap):

    for r in regions:
        logging.debug(r.centroid, costmap[r.centroid])

    return [r.label for r in sorted(regions, key=lambda x: costmap[x.centroid])]


def sort_colormap_average(regions, costmap):
    rcol = []
    for r in regions:
        regavgcolor = numpy.mean(map(lambda x: costmap[x[0], x[1]], r.coords))
        rcol.append({'label': r.label, 'averagecolor': regavgcolor})

    return [r['label'] for r in sorted(rcol, key=lambda r:r['averagecolor'])]


def map_sort_function(sortmethod):
    if sortmethod == "random":
        return None
    elif sortmethod == "avgcolor":
        return sort_colormap_average
    elif sortmethod == "centroidcolor":
        return sort_colormap_centroid
    elif sortmethod == "dist":
        return sort_regions


def segment_image(input_file, output_dir, order_function=None, colormap=None, show_images=False):
    # Open original image
    imgcolor = imageio.imread(input_file)
    # Open the grayscale version
    img = imageio.imread(input_file, as_gray=True)
    if colormap:
        costimg = imageio.imread(colormap, as_gray=True)
    else:
        costimg = None

    # Threshold
    mask = img > 10
    labeled, nlabels = measure.label(mask, return_num=True)
    labeled_color = label2rgb(labeled)
    logging.info("Found regions: {nr}".format(nr=nlabels))

    regionprop = measure.regionprops(labeled, cache=True)
    for r in regionprop:
        logging.debug("Label: {} Centroid {}".format(r.label, r.centroid))

    if show_images:
        imshow(labeled_color)
        imsave("labeled.png", labeled_color)
        imshow(imgcolor)
        #imshow(costimg)
        show()

    #labels = range(1,nlabels)
    # random.shuffle(labels)
    if order_function:
        labels = order_function(regionprop, costimg)
    else:
        labels = range(1, nlabels + 1)
        random.shuffle(labels)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def rlabel(x): return labels.index(x) if x != 0 else x
    relabelfnc = numpy.vectorize(rlabel)
    relabeled = relabelfnc(labeled)

    for i in range(1, nlabels):
        logging.info("Processing frame {i}".format(i=i))
        #threshf = lambda x: x in labels[0:i]

        def threshf(x): return x < i and x != 0
        vthres = numpy.vectorize(threshf)
        labeled_thres = vthres(relabeled)

        # Now we create a image with the alement masked

        # tuples are not mutable, we need an additional channel for alpha
        shape = list(imgcolor.shape)
        shape[2] += 1
        masked = numpy.zeros(tuple(shape), dtype=numpy.uint8)

        # Apply the mask to the three components
        masked[:, :, 0] = imgcolor[:, :, 0] * labeled_thres
        masked[:, :, 1] = imgcolor[:, :, 1] * labeled_thres
        masked[:, :, 2] = imgcolor[:, :, 2] * labeled_thres
        masked[:, :, 3] = labeled_thres * 255
        framename = '{d}/collage_{n:03d}.png'.format(d=output_dir, n=i)
        logging.info("Processing image {}".format(framename))
        imsave(framename, masked)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Input image")
    parser.add_argument('outdir', help="Output directory")
    parser.add_argument('--mask', help="Mask image")
    parser.add_argument('--delay', help="Delay between slides")
    parser.add_argument(
        '--sort',
        choices=["avgcolor", "centroidcolor", "dist", "random"],
        default="random",
        help="Region sorting method")

    # TODO: Generate slideshow

    args = parser.parse_args()

    use_plugin('gtk')
    use_plugin('pil')

    segment_image(args.input, args.outdir,
                  map_sort_function(args.sort), args.mask, show_images=True)
    generate_slideshow(
        args.outdir, '{d}/slideshow.txt'.format(d=args.outdir), args.delay)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
