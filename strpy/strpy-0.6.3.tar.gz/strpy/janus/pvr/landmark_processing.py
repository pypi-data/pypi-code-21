""" use landmark locations to estimate 3-d and pose parameters """
import numpy as np
import csv
import subprocess

import io_utils
import geometry_utils
import janus.pvr.camera_decomposition
from bobo.util import tempcsv, writecsv
import os

#camera_compute_exe = '/proj/janus/build/Debug/install/camera-compute'
camera_compute_exe = 'camera-compute'


def compute_camera(landmarks_2d_fname, landmarks_3d_fname, output_camera_fname):
    """ call external camera-compute exe """
    camera_compute_args = [camera_compute_exe, landmarks_2d_fname, landmarks_3d_fname]

    pe = subprocess.Popen(camera_compute_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = pe.communicate()
    retcode = pe.returncode
    if not retcode == 0:
        print stdout
        print stderr
        raise Exception('camera-compute failed. args = ' + str(camera_compute_args))

    with open(output_camera_fname, "w") as ofd:
        ofd.write(stdout)
    return


def aflw_landmarks_to_pose(landmarks_2d):
    """ compute camera matrix, decompose into orthographic + pose """

    aflw_landmarks_3d = np.array([[-59.5506, 34.52927, 45.95167],
                    [-38.9114875, 42.2239875, 63.5267625],
                    [-21.056375, 38.1370375, 68.5148],
                    [20.5855714286, 38.3796714286, 68.6379285714],
                    [39.225675, 41.9848375, 63.2982875],
                    [59.87481, 34.99178, 46.42763],
                    [-49.785075, 20.712625, 50.3248],
                    [-34.6487833333, 21.58165, 58.5930166667],
                    [-20.86085, 19.5610166667, 56.3544666667],
                    [19.2040333333, 19.34835, 57.12125],
                    [34.7374222222, 21.6607333333, 58.4510333333],
                    [50.2910583333, 20.9555333333, 50.2916333333],
                    [-78.579325, -24.437875, -22.6115375],
                    [-22.6565, -25.04897, 66.94048],
                    [-0.677588571429, -17.3030142857, 93.0248571429],
                    [23.13026, -24.44476, 67.00755],
                    [79.1229857143, -23.2558285714, -22.4468571429],
                    [-29.49715, -52.4265, 61.1678125],
                    [0.571118333333, -51.6207666667, 75.4856666667],
                    [30.43631, -52.66206, 60.91615],
                    [-0.414894401429, -92.3924142857, 67.3744714286]]) 

    landmarks_2d_fname = writecsv(landmarks_2d, tempcsv(), separator=' ')
    landmarks_3d_fname = writecsv(aflw_landmarks_3d.tolist(), tempcsv(), separator=' ')
    output_camera_fname = tempcsv()
    
    compute_camera(landmarks_2d_fname, landmarks_3d_fname, output_camera_fname)

    # read matrix back in, decompose, and write pose
    P = io_utils.read_matrix(output_camera_fname)

    
    K,D,R,T = janus.pvr.camera_decomposition.decompose_affine(P, verbose=False)    
    K,R,T,H = janus.pvr.camera_decomposition.affine_to_orthographic(K,R,T, limit_H_diagonal=True)
    
    # write transformed camera to file
    RT = geometry_utils.stack_RT(R,T)
    P = np.dot(np.dot(K,D),RT)

    yaw, pitch, roll = janus.pvr.camera_decomposition.decompose_camera_rotation(R)

    #with open(output_pose_fname,'wb') as pfd:
    #    writer = csv.DictWriter(pfd,('pitch','yaw','roll'),delimiter=',')
    #    writer.writeheader()
    #    writer.writerow({'pitch':pitch, 'yaw':yaw, 'roll':roll})

    return (float(pitch), float(np.sign(yaw)*(np.abs(yaw) - 180.0)), float(roll))


def compute_camera_and_pose_from_landmarks(landmarks_2d_fname, landmarks_3d_fname, output_camera_fname, output_pose_fname):
    """ compute camera matrix, decompose into orthographic + pose """
    compute_camera(landmarks_2d_fname, landmarks_3d_fname, output_camera_fname)

    # read matrix back in, decompose, and write pose
    P = io_utils.read_matrix(output_camera_fname)

    K,D,R,T = janus.pvr.camera_decomposition.decompose_affine(P)
    K,R,T,H = janus.pvr.camera_decomposition.affine_to_orthographic(K,R,T, limit_H_diagonal=True)

    # write transformed camera to file
    RT = geometry_utils.stack_RT(R,T)

    P = np.dot(np.dot(K,D),RT)

    yaw, pitch, roll = janus.pvr.camera_decomposition.decompose_camera_rotation(R)

    with open(output_pose_fname,'wb') as pfd:
        writer = csv.DictWriter(pfd,('pitch','yaw','roll'),delimiter=',')
        writer.writeheader()
        writer.writerow({'pitch':pitch, 'yaw':yaw, 'roll':roll})

    return pitch, yaw, roll


