from glob import glob
import os
import vxl
import face3d
from multiprocessing import Pool
import cv2


class dir_wrapper(object):
    def __init__(self, preproc_func, output_path, original_path, meta_path, coeffs_path, write_mask=True, redo=True, remove_alpha_only=False):
        self.output_path = output_path
        self.meta_path = meta_path
        self.coeffs_path = coeffs_path
        self.write_mask = write_mask
        self.original_path = original_path
        self.redo = redo
        self.preproc_func = preproc_func
        self.remove_alpha_only = remove_alpha_only

    def __call__(self, dir):
        files = glob(dir + '/*.png')
        all_fine = True
        for f in files:
            all_fine &= self.preproc_func(f, self.output_path, self.coeffs_path,
                                          self.meta_path, self.original_path,
                                          self.redo, self.write_mask, self.remove_alpha_only)
        return all_fine


def remove_alpha_and_save(filepath, jpeg_path, mask_path, redo=True, write_mask=True):

    if write_mask and os.path.isfile(jpeg_path) and os.path.isfile(mask_path) and not redo:
        # print "skipping image ", filepath
        return True  # break if mask file, jpeg file are present and are writing masks
    elif not write_mask and os.path.isfile(jpeg_path) and not redo:
        return True  # break if mask file, jpeg file are present and are writing masks
    try:
        im = cv2.imread(filepath, -1)
        print "Loaded image ", filepath
    except IOError:
        print "Could not read ", filepath
        return False
    if im is not None:
        if write_mask:
            cv2.imwrite(mask_path, im[:,:,3])
        cv2.imwrite(jpeg_path, im[:,:,0:3])
        return True
    else:
        print " Loaded None Image ", filepath


def add_background(filepath, output_base, coeffs_dir, meta_dir, og_dir,
                   redo=True, write_mask=True, remove_alpha_only=False):

    [base, fname] = os.path.split(filepath)
    [prefix, ext] = os.path.splitext(fname)
    [base_n, jitter_id] = os.path.split(base)
    coeffs_path = coeffs_dir + '/%s_coeffs.txt' % jitter_id
    [subject_id, sighting_id] = jitter_id.split('_')
    meta_path = meta_dir + '%s_jitter.txt' % jitter_id
    og_path = og_dir + '/%s/%s.JPEG' % (subject_id, jitter_id)
    jpeg_path = output_base + '/%s/%s.jpeg' % (jitter_id, prefix)
    mask_path = output_base + '/%s/%s_msk.png' % (jitter_id, prefix)
    if not os.path.isdir(output_base + '/%s/' % jitter_id):
        os.mkdir(output_base + '/%s/' % jitter_id)

    if not os.path.isfile(meta_path) and not os.path.isfile(coeffs_path) and not os.path.isfile(og_path)or remove_alpha_only:
        return remove_alpha_and_save(filepath, jpeg_path, mask_path, redo=redo, write_mask=write_mask)
    else:
        if os.path.isfile(jpeg_path) and not redo:
            return True
        input_coeffs = face3d.subject_ortho_sighting_coefficients(coeffs_path)
        output_coeffs = face3d.subject_ortho_sighting_coefficients(meta_path)
        img_og_vil = vxl.vil_load(og_path)
        img_jitter_vil = vxl.vil_load(filepath)
        img_out_vil = vxl.vil_image_view_byte()
        parts = prefix.split('_')
        output_index = int(parts[4])
        success = face3d.composite_background(img_og_vil, img_jitter_vil, input_coeffs.camera(0), output_coeffs.camera(output_index), img_out_vil)
        if not success:
            return remove_alpha_and_save(filepath, jpeg_path, mask_path, write_mask=write_mask, redo=redo)
#            print 'writing image with black background', jpeg_path
        else:
            try:
                vxl.vil_save(img_out_vil, jpeg_path)
#                print 'writing image with warped background', jpeg_path
                return True
            except IOError:
                print "Failed to write ", jpeg_path
                return False

output_path = '/disk1/vsi/vggface/render_background/'
nas_path = '/disk1/vsi/vggface/render/'
meta_path = '/disk1/vsi/vggface/meta/'
coeffs_path = '/disk1/vsi/vggface/coefficients/'
original_path = '/disk1/vgg-face-janus/images/'
print "Started glob"
subj_dirs = glob(nas_path + '*')
subj_dirs.sort()
print "Finished glob"
threads = Pool(16)


if __name__ == "__main__":

    results = threads.map(dir_wrapper(add_background, output_path, original_path,
                                      meta_path, coeffs_path, redo=False), subj_dirs)
