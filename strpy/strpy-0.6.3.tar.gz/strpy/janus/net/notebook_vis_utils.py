from janus.dataset.csN import Protocols
from janus.dataset.cs4 import uniq_cs4_id
from glob import glob
import janus.pvr.python_util.io_utils as io_utils
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def image_list_from_template(janus_template, chip_dir=None, cs='cs3', uniq_func=uniq_cs4_id, max_images=50):
    image_det_list = [im for m in janus_template for im in m]
    max_im = min(len(image_det_list), max_images)
    if chip_dir is None:
        return [io_utils.imread(im.filename()) for im in image_det_list[0: max_im]]
    else:
        return [io_utils.imread(os.path.join(chip_dir, '%s.png' % uniq_func(im))) for im in image_det_list[0: max_im]]

    return image_det_list


def ranked_image_list_from_template(all_templates, ptid, gtid, probe_scores=None, gallery_scores=None,
                                    probe_media=None, gallery_media=None, chip_dir=None,
                                    jittered_dir=None, scale=False, cs='cs3', uniq_func=uniq_cs4_id):
    image_det_list_probe = [im for m in all_templates[ptid] for im in m]
    image_det_list_gallery = [im for m in all_templates[gtid] for im in m]

    if probe_media is not None and gallery_media is not None and gallery_scores is not None and probe_scores is not None:
        assert(len(probe_scores) == len(gallery_media))
        assert(len(gallery_scores) == len(probe_media))


        probe_dict = {probe_m: gallery_scores[i] / (2.0 * len(gallery_scores)) if scale else gallery_scores[i] for i, probe_m in enumerate(probe_media)}
        gallery_dict = {gallery_m: probe_scores[i] / (2.0 * len(probe_scores)) if scale else probe_scores[i] for i, gallery_m in enumerate(gallery_media)}

        avg_probe_media_score = 0.0; avg_gal_media_score = 0.0
        for k in probe_dict:
            avg_probe_media_score += probe_dict[k] / (2.0 * len(gallery_scores))
        for k in gallery_dict:
            avg_gal_media_score += gallery_dict[k] / (2.0 * len(probe_scores))

        (probe_images, probe_media_scores) = zip(*[(os.path.join(chip_dir, '%s.png' % uniq_func(im)), probe_dict[im.attributes['SIGHTING_ID']]) for im in image_det_list_probe])
        (gallery_images, gallery_media_scores) = zip(*[(os.path.join(chip_dir, '%s.png' % uniq_func(im)), gallery_dict[im.attributes['SIGHTING_ID']]) for im in image_det_list_gallery])

    else:
        probe_images = [os.path.join(chip_dir, '%s.png' % uniq_func(im)) for im in image_det_list_probe]
        gallery_images = [os.path.join(chip_dir, '%s.png' % uniq_func(im)) for im in image_det_list_gallery]
        probe_media_scores = None; gallery_media_scores = None; avg_probe_media_score = None; avg_gal_media_score = None;

    return probe_images, probe_media_scores, gallery_images, gallery_media_scores, avg_probe_media_score, avg_gal_media_score


def jittered_image_list_from_template(all_templates, tid, jittered_dir=None,
                                      jitter_suffix=None, max_images=50, cs='cs3',
                                      separate_dirs=False, uniq_func=uniq_cs4_id):
    image_det_list = [im for m in all_templates[tid] for im in m]
    output = []; fnames = []
    for im in image_det_list:
        key = uniq_func(im)
        if separate_dirs:
            final_jittered_dir = os.path.join(jittered_dir, '%s' % key)
        else:
            final_jittered_dir = jittered_dir
        if jitter_suffix is None:
            jitters = glob(final_jittered_dir + "/%s_*.png" % key)
        else:
            jitters = glob(final_jittered_dir + "/%s_*_%s.png" % (key, jitter_suffix))
        fnames += jitters
    count = 0;
    for f in fnames:
        try:
            output.append(io_utils.imread(f)[:, :, 0:3])
            count += 1
        except IOError:
            output = output
        if count > max_images:
            break
    if not output:
        output.append(np.zeros((150,150), np.uint8))
    return output


def add_subgrid_with_images(image_list, fig, grid_loc, title=None, n=3, m=3, fontcolor='black', fontsize=20, columnfixed=True, readjust_gridsize=False, subtitles=None):
    if len(image_list) > n * m or not readjust_gridsize:
        rows, cols = n, m
    elif columnfixed:
        rows = int(np.ceil(len(image_list) / float(m)))
        cols = m
    else:
        cols = int(np.ceil(len(image_list) / float(m)))
        rows = n

    render_grid = matplotlib.gridspec.GridSpecFromSubplotSpec(rows, cols, subplot_spec=grid_loc, wspace=0.02, hspace=0.1)
    ax_mview = plt.subplot(grid_loc)
    if title is not None:
        ax_mview.set_title(title, fontsize=fontsize, color=fontcolor)
    ax_mview.axis('off')
    for idx in xrange(0, rows * cols):
        ax = plt.Subplot(fig, render_grid[idx])
        if subtitles is not None and idx < len(subtitles):
            ax.set_title(subtitles[idx], fontsize=int(0.7 * fontsize))
        if idx >= len(image_list):
            break;
        ax.imshow(image_list[idx], cmap=cm.gray, vmin=0, vmax=255)
        ax.axis('off')
        fig.add_subplot(ax)
