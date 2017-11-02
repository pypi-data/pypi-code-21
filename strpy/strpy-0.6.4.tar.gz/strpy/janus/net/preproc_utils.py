import os
import bobo.app
import bobo.metrics
import bobo.util
import janus.metrics
from pdb import set_trace as keyboard
import numpy as np
from  janus.dataset.cs4 import CS4
from bobo.util import Stopwatch
from pyspark import SparkContext
from janus.dataset.cs4 import uniq_cs4_id
from janus.dataset.cs3 import uniq_cs3_id
from janus.dataset.strface import uniq_strface_id
from bobo.util import writecsv

def centercrop(img, w, h):

    xmin = round(0.5 * (img.width()-w));
    ymin = round(0.5 * (img.height()-h));
    xmax = xmin + w - 1;
    ymax = ymin + h - 1;
    try:
        img.crop([xmin, ymin, xmax, ymax])
        return img
    finally:
        return img


def preprocess_im(im, dilate=1.1):
    try:
        im.crop(bbox=im.bbox.dilate(dilate)).resize(rows=512)
        return im
    except:
        print "could not crop image ", im.filename()
        return im


def chip_split(dataset_templates, outdir, dilate=1.5, name_func=uniq_cs4_id):
    # Platform initialization

    bobo.util.remkdir(outdir)

    print 'Saving to %s' % outdir

    # Dataset
    f_initialize = (lambda im: preprocess_im(im, dilate=dilate))  # preprocess images in template
    f_write = (lambda im: im.flush() if os.path.exists(os.path.join(outdir, name_func(im) + '.png'))
               else im.saveas(os.path.join(outdir, name_func(im) + '.png')).flush())
    # Evaluation splits
    with Stopwatch() as sw:
        dataset = dataset_templates.map(f_initialize).map(f_write)
        dataset.collect()


    print 'Done: Stopwatch time: %d' % int(sw.elapsed)


def split_encodefile(sid_list, N, outdir, outbasename, uniq_func, dilate=1.1):
    # Platform initialization

    L = len(sid_list)
    # Dataset
    n = int(np.ceil(L/float(N)))
    sid_list.sort(key = lambda im: uniq_func(im))
    chunks = [sid_list[i:i + n] for i in xrange(0,L,n)]
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for k, chunk in enumerate(chunks):
        if len(chunks) == 1:
            outfile = '%s.csv' % (outbasename)
        else:
            outfile = '%s_%d.csv' % (outbasename, k)
        csv_file = os.path.join(outdir, outfile)

        dilated_imset = [im.boundingbox(dilate=dilate) for im in chunk]
        lines = [(im.filename(), '%s' % uniq_func(im),
                  round(im.boundingbox().xmin), round(im.boundingbox().ymin),
                  round(im.boundingbox().width()),round(im.boundingbox().height()))
                 for im in dilated_imset]
        writecsv(lines, csv_file)
