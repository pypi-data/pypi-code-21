#!/usr/bin/env python
""" predict missing 2-d landmark locations given the visible ones """
import subprocess
import numpy as np
import tempfile
import os
import bobo.app

#default_camera_compute_exe = '/proj/janus/build/Release/tools/camera-compute'
default_camera_compute_exe = os.path.join(bobo.app.binarypath(), 'camera-compute')


def predict_missing_landmarks(landmarks_2d, landmarks_3d, camera_compute_path=default_camera_compute_exe):
    """ 2d landmarks containing nan's will be filled in based on valid ones
        returns all 2-d landmarks with missing values filled in.
    """
    # filter out invalid landmarks
    landmarks_good = [(l2d, l3d) for l2d, l3d in zip(landmarks_2d, landmarks_3d) if not np.any(np.isnan(l2d))]

    # generate temporary files containing good landmarks
    file_2d = tempfile.NamedTemporaryFile(delete=False)
    file_3d = tempfile.NamedTemporaryFile(delete=False)
    for l2d, l3d in landmarks_good:
        file_2d.write(str(l2d[0]) + ' ' + str(l2d[1]) + '\n')
        file_3d.write(str(l3d[0]) + ' ' + str(l3d[1]) + ' ' + str(l3d[2]) + '\n')
    file_2d.close()
    file_3d.close()

    try:
        camera_compute_args = [camera_compute_path, file_2d.name, file_3d.name]
        pe = subprocess.Popen(camera_compute_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = pe.communicate()
        retcode = pe.returncode
    except:
        raise ValueError('Invalid camera_compute executable "%s"' % camera_compute_path)

    # clean up temporary files
    os.remove(file_2d.name)
    os.remove(file_3d.name)

    if not retcode == 0:
        print('error: ' + stderr)
        raise Exception('camera-compute returned error')

    P = np.fromstring(stdout, sep=' ').reshape((3,4))

    landmarks_2d_good = []
    for i in range(len(landmarks_2d)):

        if np.any(np.isnan(landmarks_2d[i])):
            l3dh = np.array((landmarks_3d[i][0], landmarks_3d[i][1], landmarks_3d[i][2], 1.0))
            l2dh = np.dot(P, l3dh)
            l2d = np.array((l2dh[0]/l2dh[2], l2dh[1]/l2dh[2]))
        else:
            l2d = landmarks_2d[i]

        landmarks_2d_good.append(l2d)

    return np.array(landmarks_2d_good)

