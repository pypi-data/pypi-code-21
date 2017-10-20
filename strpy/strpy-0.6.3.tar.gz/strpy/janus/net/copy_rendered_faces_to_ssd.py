from glob import glob
import os
import cv2
from multiprocessing import Pool
from add_background_to_pose_jittered_images import dir_wrapper, add_background
nas_path = '/proj/janus3/vsi/vggface/render/'
output_path = '/disk1/vsi/vggface/render/'
meta_path = '/disk1/vsi/vggface/meta/'
coeffs_path = '/disk1/vsi/vggface/coefficients/'
original_path = '/disk1/vgg-face-janus/images/'

# prev_proc = 0.0
# for i, dirs in enumerate(subj_dirs):
#     files = glob(dirs + '/*.png')
#     map(lambda im: compress_and_remove_background(im, output_path), files)
#     curr_proc = 100 * i / float(len(subj_dirs))
#     if curr_proc > prev_proc + 0.05:
#         prev_proc = curr_proc
#         print "Finished %.2f %%" % curr_proc

print "Started glob"
subj_dirs = glob(nas_path + '*')
subj_dirs.sort()
print "Finished glob"
threads = Pool(16)

if __name__ == "__main__":

    results = threads.map(dir_wrapper(add_background, output_path,
                                      original_path, meta_path, coeffs_path, redo=False,
                                      remove_alpha_only=True), subj_dirs)
