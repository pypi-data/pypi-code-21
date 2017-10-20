#!/usr/bin/env python
""" convert a mesh to a PVR voxel model """
import boxm2_register
import boxm2_mesh_adaptor
import boxm2_scene_adaptor
import generate_scene_xml_from_mesh
import os
import glob
import argparse


def PVR_from_mesh(mesh_filename, model_base_dir, num_blocks, max_num_subblocks, appearance_models, num_bins, max_level, refine_its=1, lvcs_origin=None, occupied_prob=0.99, create_base_dir=True, prompt_before_delete=True):
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
    generate_scene_xml_from_mesh.generate_scene_xml_from_mesh(mesh_filename, scene_xml, model_dir_rel, num_blocks, max_num_subblocks, appearance_models, num_bins, max_level, lvcs_origin)
    print('..Done.')

    print('Creating scene adaptor..')
    #gpu_str = 'gpu' + str(gpu_idx)
    cpp_str = 'cpp'
    scene = boxm2_scene_adaptor.boxm2_scene_adaptor(scene_xml, device_string=cpp_str)
    print('..Done.')

    print('Importing mesh..')
    boxm2_mesh_adaptor.import_triangle_mesh(scene.scene, scene.active_cache, mesh_filename, occupied_prob)
    print('..Done. Out of Loop')

    for it in range(refine_its):
        print('refining.. iteration '+str(it))
        scene.refine(thresh=0.3, device_string=cpp_str)
        print('..Done.')

        print('Importing mesh..')
        boxm2_mesh_adaptor.import_triangle_mesh(scene.scene, scene.active_cache, mesh_filename, occupied_prob)
        print('..Done. iteration '+str(it))

    print(' writing cache..')
    scene.write_cache()
    print('..done')

def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('mesh_filename')
    parser.add_argument('--model_dir', default='.')
    parser.add_argument('--num_blocks', nargs=3, type=int, default=(1,1,1))
    parser.add_argument('--max_num_subblocks', type=int, default=100)
    parser.add_argument('--appearance_models', nargs='+', default=('boxm2_mog3_grey',))
    parser.add_argument('--num_bins', type=int, default=1)
    parser.add_argument('--max_level', type=int, default=4)
    parser.add_argument('--refine_its', type=int, help='Number of refine iterations', default=1)
    parser.add_argument('--lvcs_origin', nargs=3, type=float, help='LVCS origin in form lon lat hae', default=None)
    parser.add_argument('--occupied_prob',type=float,default=0.99)
    args = parser.parse_args()

    PVR_from_mesh(args.mesh_filename, args.model_dir, args.num_blocks, args.max_num_subblocks, args.appearance_models, args.num_bins, args.max_level, args.refine_its, args.lvcs_origin, args.occupied_prob, create_base_dir=True, prompt_before_delete=False)


if __name__ == '__main__':
    main()
