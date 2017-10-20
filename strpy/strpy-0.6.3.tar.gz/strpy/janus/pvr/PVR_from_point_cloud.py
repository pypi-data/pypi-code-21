#!/usr/bin/env python
""" convert a point cloud to a PVR voxel model """
import boxm2_register
import boxm2_mesh_adaptor
import boxm2_scene_adaptor
import mesh_utils
import io_utils
import tempfile
import generate_scene_xml_from_ply
import os
import glob
import argparse


def PVR_from_point_cloud(ply_filename, model_base_dir, num_blocks, max_num_subblocks, appearance_models, num_bins, max_level, refine_its=1, lvcs_origin=None, create_base_dir=True, prompt_before_delete=True):
    """ create and update the boxm2 model """

    if not os.path.exists(model_base_dir):
        if create_base_dir:
            os.mkdir(model_base_dir)
        else:
            raise Exception('Model base dir ' + model_base_dir + ' does not exist.')

    model_dir_rel = 'model'
    model_dir = model_base_dir + '/' + model_dir_rel
    scene_xml = model_base_dir + '/scene.xml'
    if not os.path.isdir(model_dir):
        os.mkdir(model_dir)
    else:
        if prompt_before_delete:
            _ = raw_input('Will remove all *.bin files in ' + model_dir + '.  Press Enter to Continue')
        model_files = glob.glob(model_dir + '/*.bin')
        for binfile in model_files:
            os.remove(binfile)

    print('Initializing Model..')
    generate_scene_xml_from_ply.generate_scene_xml_from_ply(ply_filename, scene_xml, model_dir_rel, num_blocks, max_num_subblocks, appearance_models, num_bins, max_level, lvcs_origin)
    print('..Done.')

    # convert the ply2 file to XYZ in a temporary file
    temp_dir = tempfile.mkdtemp()
    verts = mesh_utils.get_ply_vertices(ply_filename)
    xyz_filename = temp_dir + '/verts.xyz'
    io_utils.write_matrix(verts.transpose(), xyz_filename)
    print( 'writing %d vertices to %s' % (verts.shape[1], xyz_filename) )

    print('Creating scene adaptor..')
    #gpu_str = 'gpu' + str(gpu_idx)
    cpp_str = 'cpp'
    scene = boxm2_scene_adaptor.boxm2_scene_adaptor(scene_xml, device_string=cpp_str)
    print('..Done.')

    for it in range(refine_its):

        if it > 0:
            print('refining..')
            scene.refine(thresh=0.3, device_string=cpp_str)
            print('..Done.')

        print('Importing point cloud..')
        boxm2_mesh_adaptor.import_point_cloud(scene.scene, scene.active_cache, xyz_filename, min_octree_depth=0)
        print('..Done.')

    print(' writing cache..')
    scene.write_cache()
    print('..done')

    print('cleaning up temporary files..')
    os.remove(xyz_filename)
    os.rmdir(temp_dir)
    print('..done')

def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('ply_filename')
    parser.add_argument('--model_dir', default='.')
    parser.add_argument('--num_blocks', nargs=3, type=int, default=(1,1,1))
    parser.add_argument('--max_num_subblocks', type=int, default=100)
    parser.add_argument('--appearance_models', nargs='+', default=('boxm2_mog3_grey',))
    parser.add_argument('--num_bins', type=int, default=1)
    parser.add_argument('--max_level', type=int, default=3)
    parser.add_argument('--refine_its', type=int, help='Number of refine iterations', default=1)
    parser.add_argument('--lvcs_origin', nargs=3, type=float, help='LVCS origin in form lon lat hae', default=None)
    args = parser.parse_args()

    PVR_from_point_cloud(args.ply_filename, args.model_dir, args.num_blocks, args.max_num_subblocks, args.appearance_models, args.num_bins, args.max_level, args.refine_its, args.lvcs_origin, create_base_dir=True, prompt_before_delete=True)


if __name__ == '__main__':
    main()
