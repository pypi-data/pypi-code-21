#!/usr/bin/env python
""" methods for filling in missing data and generating confidence masks """
import argparse

import io_utils
import numpy as np
import skimage.filter
import skimage.morphology
import camera_decomposition
import camera_utils
import image_utils

def finalize_frontalization(frontalized_in, fg_mask, vis_mask, sigmoid_scale=20.0, sigmoid_offset=0.75, fill_wmirror=True):
    """ fill in missing data via symmetry """
    vis_mask_smooth = skimage.filter.rank.median(vis_mask, skimage.morphology.disk(15)).astype('float') / 255.0
    weight_img  = 1.0 / (1.0 + np.exp(-sigmoid_scale * (vis_mask_smooth-sigmoid_offset)))
    if fill_wmirror:
        mirrored = frontalized_in[:,::-1]
        frontalized_wsym = frontalized_in[:,:] * (fg_mask > 127)
        fill_mask = (weight_img < weight_img[:,::-1]) & (weight_img < 0.75)  & (fg_mask > 127)
        frontalized_wsym[fill_mask] = mirrored[fill_mask]*(1-weight_img[fill_mask]) + frontalized_wsym[fill_mask]*weight_img[fill_mask]
    else:
        frontalized_wsym = frontalized_in

    mask_out = (weight_img * fg_mask.astype(np.float)/255.0)
    return frontalized_wsym, (mask_out*255).astype(np.uint8)


def add_context(frontalized_img, og_img, fg_mask, frontal_camera, og_camera):
    """ warp original image to give context around frontalized head """
    _,_,R,_ = camera_decomposition.decompose_affine(og_camera.P)
    frontal_plane_og = np.array((0,0,-30))
    frontal_plane_z = -R[2,:]
    frontal_plane_x = np.cross( np.array((0,1,0)), frontal_plane_z)
    frontal_plane_y = np.cross( frontal_plane_z, np.array((1,0,0)) )

    invH1 = og_camera.plane2image(frontal_plane_og, frontal_plane_x, frontal_plane_y)
    invH2 = frontal_camera.image2plane(frontal_plane_og, frontal_plane_x, frontal_plane_y)
    invH = np.dot(invH1,invH2)

    warped = image_utils.sample_patch_projective(og_img, invH, frontalized_img.shape[0:2])
    warped[np.isnan(warped)] = 0.0
    if len(warped.shape) > 2:
        warped_bw = image_utils.rgb2gray(warped)
    else:
        warped_bw = warped

    sigmoid_offset=0.5
    sigmoid_scale = 20.0
    weight_img  = 1.0 / (1.0 + np.exp(-sigmoid_scale * (fg_mask-sigmoid_offset)))
    blended = frontalized_img * weight_img + warped_bw * (1.0 - weight_img)
    blended[blended > 1.0] = 1.0
    blended[blended < 0.0] = 0.0

    return blended


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('frontalized_raw_fname')
    parser.add_argument('fg_mask_fname')
    parser.add_argument('vis_mask_fname')
    parser.add_argument('original_img_fname')
    parser.add_argument('original_camera_fname')
    parser.add_argument('frontal_camera_fname')
    parser.add_argument('frontalized_out_fname')
    parser.add_argument('mask_out_fname')
    parser.add_argument('--add_context',type=bool,default=False)
    args = parser.parse_args()

    frontalized_in = io_utils.imread(args.frontalized_raw_fname)
    fg_mask = io_utils.imread(args.fg_mask_fname)
    vis_mask = io_utils.imread(args.vis_mask_fname)

    frontalized_wsym, mask_out = finalize_frontalization(frontalized_in, fg_mask, vis_mask)

    if args.add_context:
        og_img = io_utils.imread(args.original_img_fname).astype(np.float) / 255
        frontal_camera = camera_utils.ProjectiveCamera(io_utils.read_matrix(args.frontal_camera_fname))
        og_camera = camera_utils.ProjectiveCamera(io_utils.read_matrix(args.original_camera_fname))
        frontalized_out = add_context(frontalized_wsym.astype(np.float)/255, og_img, fg_mask.astype(np.float)/255, frontal_camera, og_camera)

        frontalized_out = (frontalized_out * 255).astype(np.uint8)
    else:
        frontalized_out = frontalized_wsym

    io_utils.imwrite(frontalized_out, args.frontalized_out_fname)
    io_utils.imwrite(mask_out, args.mask_out_fname)

if __name__ == '__main__':
    main()
