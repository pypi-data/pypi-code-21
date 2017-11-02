#!/usr/bin/env python
""" methods for frontalizing faces """
import argparse

import geometry_utils
import image_utils
import io_utils


def frontalize_affine_2d(landmarks_img, landmarks_target, img, target_img_shape):
    """ frontalize a face based on optimal 2-d affine tranformation """
    H_landmarks = geometry_utils.compute_2D_affine_xform(landmarks_target, landmarks_img)
    frontal_img = image_utils.sample_patch_projective(img, H_landmarks, target_img_shape)
    return frontal_img


def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument('landmarks_img_filename')
    parser.add_argument('landmarks_target_filename')
    parser.add_argument('image_filename')
    parser.add_argument('target_img_nx')
    parser.add_argument('target_img_ny')
    parser.add_argument('output_filename')
    args = parser.parse_args()

    target_img_shape = (args.target_img_ny, args.target_img_nx)  # rows, cols

    # load landmarks
    landmarks_M = io_utils.read_matrix(args.landmarks_img_filename)
    landmarks = [(landmarks_M[i,0], landmarks_M[i,1]) for i in range(landmarks_M.shape[0])]

    landmarks_target_M = io_utils.read_matrix(args.landmarks_target_filename)
    landmarks_target = [(landmarks_target_M[i,0], landmarks_target_M[i,1]) for i in range(landmarks_target_M.shape[0])]

    face_img = io_utils.imread(args.image_filename)

    frontalized_2d = frontalize_affine_2d(landmarks, landmarks_target, face_img, target_img_shape)

    # write out output
    io_utils.imwrite(frontalized_2d, args.output_filename)

