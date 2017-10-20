#!/usr/bin/env python
""" generate camera model for blender rendered images """
import geometry_utils
import numpy as np
import argparse
import sys


def generate_blender_camera(yaw_degs, pitch_degs, roll_degs, scale=250.0, img_shape=(500,500), T0=(0,0,0)):
    """ generate an affine camera model for a blender orthographic projection """
    K = np.zeros((3,3))
    K[0,0] = img_shape[1] / float(scale)
    K[1,1] = K[0,0]
    K[2,2] = 1.0
    K[0,2] = img_shape[1] / 2.0
    K[1,2] = img_shape[0] / 2.0

    DropZ = np.zeros((3,4))
    DropZ[0,0] = DropZ[1,1] = DropZ[2,3] = 1.0

    R0 = np.diag((1.0, -1.0, -1.0))

    yaw = np.deg2rad(yaw_degs)
    pitch = np.deg2rad(pitch_degs)
    roll = np.deg2rad(roll_degs)
    Rhead = geometry_utils.Euler_angles_to_matrix(yaw,pitch,roll,order='YXZ')

    print('Rhead = \n' + str(Rhead))
    Rcam = np.dot( R0, Rhead )
    #Rcam = np.dot(R0, R.transpose())
    #Rcam = np.dot( R0, R )

    T0 = np.array(T0)

    #print('Rhead = ' + str(Rhead))
    #print('R0 = ' + str(R0))
    #print('R = ' + str(R))

    RT = geometry_utils.stack_RT(Rcam, np.dot(Rcam,T0))

    P = np.dot(np.dot(K, DropZ), RT)

    cam_loc0 = np.array((0.0, 0.0, 500.0))
    cam_loc = np.dot(Rhead.transpose(), cam_loc0)

    #return P
    return P,Rcam,cam_loc


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('--scale', type=float, default=250.0)
    parser.add_argument('--size', nargs=2, type=int, default=(500,500), help='img_width img_height')
    parser.add_argument('--yaw', type=float, default=0.0)
    parser.add_argument('--pitch', type=float, default=0.0)
    parser.add_argument('--roll', type=float, default=0.0)
    parser.add_argument('output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    P = generate_blender_camera(yaw_degs=args.yaw, pitch_degs=args.pitch, roll_degs=args.roll, scale=args.scale, img_shape=args.size)
    for r in range(P.shape[0]):
        for c in range(P.shape[1]):
            args.output_file.write('%f ' % P[r,c])
        args.output_file.write('\n')

if __name__  == '__main__':
    main()




