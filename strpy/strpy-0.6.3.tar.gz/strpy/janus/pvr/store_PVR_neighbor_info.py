#!/usr/bin/env python
""" convert a point cloud to a PVR voxel model """
import boxm2_smart_register
import boxm2_scene_adaptor
import argparse


def store_neighbor_info(boxm2_scene):
    """ Store neighborhood info """
    boxm2_scene.cache_neighbor_info()
    boxm2_scene.write_cache()


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('model_xml_path')
    parser.add_argument('gpu_idx', type=int)
    args = parser.parse_args()

    gpu_str = 'gpu' + str(args.gpu_idx)
    boxm2_scene = boxm2_scene_adaptor.boxm2_scene_adaptor(args.model_xml_path, device_string=gpu_str)
    store_neighbor_info(boxm2_scene)


if __name__ == '__main__':
    main()
