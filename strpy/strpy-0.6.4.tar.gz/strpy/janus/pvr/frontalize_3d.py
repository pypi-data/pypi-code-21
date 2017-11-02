#!/usr/bin/env python
""" methods for frontalizing faces """
import tempfile
import os
import argparse

import io_utils

import boxm2_scene_adaptor
import vpgl_adaptor
import vil_adaptor


def complete_with_symmetry(img, vis):
    """ fill in gaps using symmetry constraint """
    ni = img.shape[1]
    img[vis > 0.5] = 1.0

    vis_mask = img > 0.05

    mirrored = img[:,ni-1::-1]
    img_out = img.copy()
    img_out[~vis_mask] = mirrored[~vis_mask]

    return img_out


def frontalize_3d(img_filename, camera_filename, target_camera_fname, target_img_shape, boxm2_scene, output_filename):
    """ frontalize the face based on backprojection / reprojection """

    vil_img, chip_ni, chip_nj = vil_adaptor.load_image(img_filename)
    vpgl_cam = vpgl_adaptor.load_affine_camera(camera_filename)
    cam_gen = vpgl_adaptor.persp2gen(vpgl_cam, chip_ni, chip_nj)

    print('updating appearance model..')
    boxm2_scene.update_app(cam_gen, vil_img)
    print('..done')

    vpgl_target_cam = vpgl_adaptor.load_affine_camera(target_camera_fname)
    target_cam_gen = vpgl_adaptor.persp2gen(vpgl_target_cam, target_img_shape[1], target_img_shape[0])

    expimg, visimg = boxm2_scene.render_vis(target_cam_gen, ni=target_img_shape[1], nj=target_img_shape[0])

    tmp_img_fname = tempfile.mktemp(suffix='.tiff', prefix='target_img_')
    tmp_vis_fname = tempfile.mktemp(suffix='.tiff', prefix='target_vis_')

    vil_adaptor.save_image(expimg, tmp_img_fname)
    vil_adaptor.save_image(visimg, tmp_vis_fname)

    reprojected_img = io_utils.imread(tmp_img_fname)
    reprojected_vis = io_utils.imread(tmp_vis_fname)

    frontalized_3d = complete_with_symmetry(reprojected_img, reprojected_vis)

    # write to disk
    io_utils.imwrite_byte(frontalized_3d, 0, 1, output_filename)

    # delete temporary files
    os.remove(tmp_img_fname)
    os.remove(tmp_vis_fname)

    return


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('img_filename')
    parser.add_argument('camera_filename')
    parser.add_argument('target_camera_filename')
    parser.add_argument('target_img_nx', type=int)
    parser.add_argument('target_img_ny', type=int)
    parser.add_argument('boxm2_scene_xml_filename')
    parser.add_argument('output_filename')
    parser.add_argument('--gpu', default='gpu0')
    args = parser.parse_args()

    target_img_shape = (args.target_img_ny, args.target_img_nx)  # rows, cols

    scene = boxm2_scene_adaptor.boxm2_scene_adaptor(args.boxm2_scene_xml_filename, device_string=args.gpu)

    frontalize_3d(args.img_filename, args.camera_filename, args.target_camera_filename, target_img_shape, scene, args.output_filename)


if __name__ == '__main__':
    main()
