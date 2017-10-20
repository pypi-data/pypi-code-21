#!/usr/bin/env python
""" convert a point cloud to a PVR voxel model """
import boxm2_smart_register
import boxm2_scene_adaptor
import vpgl_adaptor
import vil_adaptor
import io_utils
import camera_decomposition
import argparse


def paint_PVR_model(boxm2_scene, image_filename_list, camera_filename_list):
    """ update the boxm2 model appearance with each of the images """

    if not len(image_filename_list) == len(camera_filename_list):
        raise Exception('expecting same number of image and camera filenames')

    for img_fname, cam_fname in zip(image_filename_list, camera_filename_list):

        vil_img, chip_ni, chip_nj = vil_adaptor.load_image(img_fname)

        # load camera to get look direction
        P = io_utils.read_matrix(cam_fname)
        _,_,R,_ = camera_decomposition.decompose_affine(P)
        # 3rd row of rotation matrix is camera z axis in world coordinate system
        look_dir = R[2,:]

        affine_cam = vpgl_adaptor.load_affine_camera(cam_fname, look_dir=look_dir)

        gen_cam = vpgl_adaptor.persp2gen(affine_cam, chip_ni, chip_nj)

        # force painting of greyscale appearance model since interpolation cannot yet handle rgb.
        # After optimization, the rgb appearance model will be painted
        boxm2_scene.update_app(gen_cam, vil_img, force_grey=True)

    boxm2_scene.write_cache()


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('model_xml_path')
    parser.add_argument('--images', nargs='+')
    parser.add_argument('--cameras', nargs='+')
    parser.add_argument('--gpu_idx', nargs='?', type=int, default=0)
    args = parser.parse_args()
    gpu_str = 'gpu' + str(args.gpu_idx)
    boxm2_scene = boxm2_scene_adaptor.boxm2_scene_adaptor(args.model_xml_path, device_string=gpu_str)

    paint_PVR_model(boxm2_scene, args.images, args.cameras)


if __name__ == '__main__':
    main()
