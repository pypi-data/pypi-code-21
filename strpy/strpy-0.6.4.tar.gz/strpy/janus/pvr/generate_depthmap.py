#!/usr/bin/env python
""" render a depthmap """
import boxm2_register
import boxm2_scene_adaptor
import vil_adaptor
import vpgl_adaptor
import argparse
import io_utils


def render_depth(scene_path,image_width, image_height, output_filename, perspective_camera_filename=None, affine_camera_filename=None):
    """ render the depth image """
    #initialize a GPU
    print('Creating scene adaptor..')
    scene = boxm2_scene_adaptor.boxm2_scene_adaptor(scene_path, "gpu0")
    print('..Done.')

    if perspective_camera_filename is not None:
        pcam = vpgl_adaptor.load_perspective_camera(perspective_camera_filename)
    if affine_camera_filename is not None:
        pcam = vpgl_adaptor.load_affine_camera(affine_camera_filename)

    gcam = vpgl_adaptor.persp2gen(pcam, image_width, image_height)

    dexp,var,vis = scene.render_depth(gcam, image_width, image_height)
    vil_adaptor.save_image(dexp, output_filename)
    #vil_adaptor.save_image(vis, vis_fname)
    #vil_adaptor.save_image(var, var_fname)
    boxm2_register.remove_data(dexp.id)
    boxm2_register.remove_data(var.id)
    boxm2_register.remove_data(vis.id)

    boxm2_register.remove_data(pcam.id)
    boxm2_register.remove_data(gcam.id)


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('scene_path')
    parser.add_argument('--perspective', default=None)
    parser.add_argument('--affine', default=None)
    parser.add_argument('--dims_of', default=None)
    parser.add_argument('--width', type=int, default=None)
    parser.add_argument('--height', type=int, default=None)
    parser.add_argument('output_filename')
    args = parser.parse_args()

    if args.dims_of is not None:
        img = io_utils.imread(args.dims_of)
        image_width = img.shape[1]
        image_height = img.shape[0]
    else:
        if args.width is None or args.height is None:
            raise Exception('Specifiy image width and height via --dims_of <image name> or --width <w> --height <h>')
        image_width = args.width
        image_height = args.height

    render_depth(args.scene_path, image_width, image_height, args.output_filename, perspective_camera_filename=args.perspective, affine_camera_filename=args.affine)


if __name__ == '__main__':
    main()
