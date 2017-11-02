#!/usr/bin/env python
import os.path
import os
import sys
import shutil
import subprocess
from subprocess import STDOUT, CalledProcessError
import csv
import glob
import numpy as np
import strpy.bobo.util
import tempfile

import strpy.bobo.app
from strpy.bobo.util import remkdir, quietprint, temppng, filebase
from strpy.bobo.image import Image


# Keep imports here to support PVR-less builds
try:    
    import geometry_utils
    import io_utils
    from janus.pvr import landmark_processing
    from janus.pvr import camera_decomposition
    from janus.pvr import PVR_from_point_cloud
    from janus.pvr import paint_PVR_model
    from janus.pvr import generate_blender_camera
except ImportError, e:
    pass  # WARNING: will fail silently


class Frontalizer(object):
    def __init__(self, gpu_idx=0, cache_root=None,
                target_img_nx=150, target_img_ny=150, dataset=None, model_subdir='20150707',
                generate_frontalization="as_needed", use_category_subdirs=False):
        self.gpu_idx = str(gpu_idx)
        self.cache_root = cache_root if cache_root else bobo.app.logs()
        self.dataset = dataset

        self.target_img_nx = target_img_nx
        self.target_img_ny = target_img_ny

        self.pvr_python_dir = os.path.join(bobo.app.release(), 'janus', 'pvr')

        self.output_base_dir = os.path.join(self.cache_root, 'pvr', 'frontalized')

        # frontalization(_raw) and meta dirs
        self._set_subdir('')

        # models
        self.source_pvr_model = os.path.join(bobo.app.models(), 'pvr', model_subdir, 'mean_face_%d' % target_img_nx, 'scene.xml')
        self.target_pvr_model = os.path.join(bobo.app.models(), 'pvr', model_subdir, 'target_face_%d' % target_img_nx, 'scene.xml')

        # DLib landmark model file
        self.landmark_model_dir = os.path.join(bobo.app.models(), 'dlib')
        self.shape_predictor = None

        # miscellaneous
        self.generate_frontalization = generate_frontalization
        self.use_category_subdirs = use_category_subdirs

    def _get_pose_bins(self, pyr, bin_size, startframe):
        pyr_rounded = np.round(pyr/bin_size)*bin_size
        quietprint('[janus.frontalize.Frontalizer] _get_pose_bins: bin size %f'%bin_size, verbosity=2)
        bins = {}
        for j,p in enumerate(pyr_rounded,startframe):
            if np.any(np.isnan(p)): continue
            bins[tuple(p)] = j
        quietprint('[janus.frontalize.Frontalizer] _get_pose_bins: ended up with %i bins'%len(bins),verbosity=2)
        return bins

    def subsample_video_by_pose(self, vid, draw_landmarks=False, set_attributes=False,
            pose_min_bin_size=10.0, max_pose_bins=16):
        if self.use_category_subdirs:
            self._set_subdir(iter(vid).next().category())

        keep_inds_fname = os.path.join(self.meta_dir, vid[0].attributes['MEDIA_ID'] + '_subsample_frames.txt')

        if self.generate_frontalization == 'always' or \
                (self.generate_frontalization == 'as_needed' and not bobo.util.isfile(keep_inds_fname)):
            pyr = []
            for f in vid:
                pose = self.estimate_pose(f, draw_landmarks=draw_landmarks, set_attributes=set_attributes)
                pyr.append(pose)
            pyr = np.array(pyr)
         
            bins = self._get_pose_bins(pyr, pose_min_bin_size, vid._startframe)
            if len(bins) > max_pose_bins:
                quietprint('[janus.frontalize.Frontalizer.subsample_video_by_pose] Ended up with too many bins %i'%len(bins), verbosity=2)
                bins = self._get_pose_bins(pyr, pose_min_bin_size * len(bins) / max_pose_bins, vid._startframe)
            keep_inds = sorted(bins.values())
            quietprint('[janus.frontalize.Frontalizer.subsample_video_by_pose] Writing %i subsampled frame indices to %s'%(len(keep_inds), keep_inds_fname), verbosity=2)
            with open(keep_inds_fname, 'w') as f: f.write(" ".join(map(str, keep_inds)))
        elif bobo.util.isfile(keep_inds_fname):
            quietprint('[janus.frontalize.Frontalizer.subsample_video_by_pose] Reading subsampled frame indices from %s'%(keep_inds_fname), verbosity=2)
            with open(keep_inds_fname, 'r') as f: keep_inds = map(int, f.readline().split())
        else:
            assert self.generate_frontalization == 'never'
            quietprint('[janus.frontalize.Frontalizer.subsample_video_by_pose] WARN: no subsampling performed. Returning whole video clone',verbosity=2)
            return vid.clone()

        vid2 = vid.clone()
        vid2.frames(newframes = [vid2[ind] for ind in keep_inds])
        vid2._startframe = 0
        #vid2.setattribute('bins',bins)
        vid2.setattribute('kept_frame_indices', keep_inds)
        return vid2


    def estimate_pose(self, im, subdir=None, draw_landmarks=False, set_attributes=False):
        if subdir:
            self._set_subdir(subdir)

        landmarks_aflw_fname, cam_fname, pose_fname = self._get_chip_relative_fnames(im.filename(),
                self.meta_dir, '_aflw_2d_landmarks.txt', '_camera.txt', '_pose.csv')

        if self.generate_frontalization == 'never' or self.generate_frontalization == 'as_needed':
            if bobo.util.isfile(pose_fname):
                # no need to generate not new estimate
                with open(pose_fname, 'r') as f:
                    dr = csv.DictReader(f)
                    pyr = dr.next()
                pitch = float(pyr['pitch'])
                yaw = float(pyr['yaw'])
                roll = float(pyr['roll'])
                return pitch,yaw,roll
            elif self.generate_frontalization == 'never':
                # couldn't load pose from file
                return np.nan,np.nan,np.nan

        landmarks_dlib = self._estimate_dlib_landmarks(im)
        landmarks_aflw = self._dlib_to_aflw_landmarks(landmarks_dlib)
        self._write_2d_landmarks(landmarks_aflw, landmarks_aflw_fname)
        pitch, yaw, roll = landmark_processing.compute_camera_and_pose_from_landmarks(
                landmarks_aflw_fname, self.mean_face_aflw_3d_landmarks_fname, cam_fname, pose_fname)

        if set_attributes:
            #im.attributes['landmarks_dlib_fname'] = landmarks_dlib_fname
            im.attributes['landmarks_aflw_fname'] = landmarks_aflw_fname
            im.attributes['camera_fname'] = cam_fname
            im.attributes['pose_fname'] = pose_fname
            im.attributes['pitch'] = pitch
            im.attributes['yaw'] = yaw
            im.attributes['roll'] = roll

        if draw_landmarks:
            fname1, fname2 = self._get_chip_relative_fnames(im.filename(),
                self.landmarks_dir, '_dlib_landmarks.png', '_aflw_landmarks.png')
            im_dlib = self._draw_landmarks(im, landmarks_dlib)
            im_aflw = self._draw_landmarks(im, landmarks_aflw)
            im_dlib.saveas(fname1);  print 'saving "%s"' % fname1;
            im_aflw.saveas(fname2);  print 'saving "%s"' % fname2;

            if set_attributes:
                im.attributes['im_landmarks_dlib_fname'] = fname1
                im.attributes['im_landmarks_aflw_fname'] = fname2

        return pitch,yaw,roll

    def _init_dlib(self):
        """ one-time initialization """
        import dlib
        if self.shape_predictor is None:
            landmarks_fname = os.path.join(self.landmark_model_dir, "shape_predictor_68_face_landmarks.dat")
            quietprint('[janus.frontalize.Frontalizer._estimate_dlib_landmarks] Loading dlib landmarks from "%s"'%landmarks_fname)
            self.shape_predictor = dlib.shape_predictor(landmarks_fname)

            landmarks_fname = os.path.join(bobo.app.release(), 'components', 'pvr', 'data', 'mean_face_aflw_3d_landmarks.txt')
            quietprint('[janus.frontalize.Frontalizer._estimate_dlib_landmarks] Loading AFLW 3D landmarks from "%s"'%landmarks_fname)
            self.mean_face_aflw_3d_landmarks_fname = landmarks_fname
            self.mean_face_aflw_3d_landmarks = []
            with open(landmarks_fname, 'r') as f:
                for line in f.readlines():
                    self.mean_face_aflw_3d_landmarks.append(map(float, line.split()))
            self.mean_face_aflw_3d_landmarks = np.array(self.mean_face_aflw_3d_landmarks)

    def _estimate_dlib_landmarks(self, im):
        import dlib
        self._init_dlib()

        """ real work of this method """
        drect = dlib.rectangle(*map(lambda f: int(round(f)), (im.bbox.xmin, im.bbox.ymin, im.bbox.xmax, im.bbox.ymax)))
        ddet = self.shape_predictor(im.load(), drect)
        landmarks = np.array([(pt.x,pt.y) for pt in ddet.parts()])
        return landmarks

    def _dlib_to_aflw_landmarks(self, landmarks):
        import numpy as np
        def center(*indexes):
            return np.mean(landmarks[indexes,:],axis=0)

        # augment landmarks with centers of a couple of groups
        land2 = np.vstack((landmarks,
            [-1,-1],                # placeholder for bogus points
            center(19,20),          # left eyebrow center
            center(23,24),          # right eyebrow center
            center(37,38,40,41),    # left eye center
            center(43,44,46,47),    # right eye center
            center(62,66)))         # mouth center

        aflw = land2[[
            18, #  0 - left eyebrow left corner
            -5, #  1 - left eyebrow center
            21, #  2 - left eyebrow right corner
            22, #  3 - right eyebrow left corner
            -4, #  4 - right eyebrow center
            25, #  5 - right eyebrow right corner
            36, #  6 - left eye left corner
            -3, #  7 - left eye center
            39, #  8 - left eye right corner
            42, #  9 - right eye left corner
            -2, # 10 - right eye center
            45, # 11 - right eye right corner
            -6, # 12 - left earlobe SKIP
            31, # 13 - nose left corner
            30, # 14 - nose center
            35, # 15 - nose right corner
            -6, # 16 - right earlobe SKIP
            48, # 17 - mouth left corner
            -1, # 18 - mouth center
            54, # 19 - mouth right corner
             8, # 20 - chin
             ],:]
        return aflw

    def _write_2d_landmarks(self, landmarks, fname):
        with open(fname, "w") as f: f.write("".join("%f %f\n"%(x,y) for (x,y) in landmarks))

    def _draw_landmarks(self, im, landmarks, with_lines=False):
        import matplotlib.pyplot as plt
        import numpy as np

        # 3-channel grayscale, float format
        im = im.clone().grayscale().rgb()
        if im.data.dtype == np.uint8:
            im = im.float(scale=1.0/255.0)

        # count landmarks
        n,d = landmarks.shape
        assert d == 2

        # generate colors
        colors = plt.cm.jet(np.linspace(0,1,n))

        inbounds = lambda x,width: (0 <= x < width)
        inbounds1 = lambda x,width: (1 <= x < width-1)

        # plot landmarks as big squares
        loc_col = zip(landmarks, colors)
        for ((x,y),(r,g,b,a)) in loc_col:
            if not inbounds1(x,im.width()) or not inbounds1(y,im.height()): continue
            for dx in xrange(-1,2):
                for dy in xrange(-1,2):
                    im.data[y+dy,x+dx,:] = [r,g,b]

        # draw lines connecting landmarks
        if with_lines:
            for i in xrange(n-1):
                ((x0,y0), (r0,g0,b0,_)) = loc_col[i]
                if inbounds(x0,im.width()) and inbounds(y0,im.height()):
                    break;
            j = i+1
    
            while j < len(loc_col):
                ((x0,y0), (r0,g0,b0,_)) = loc_col[i]
                ((x1,y1), (r1,g1,b1,_)) = loc_col[j]
                if not inbounds(x1,im.width()) or not inbounds(y1,im.height()):
                    j = j+1
                    continue
                else:
                    i,j = j,j+1
                m = np.maximum(abs(x1-x0), abs(y1-y0)) * 2
                x = np.linspace(x0,x1,m)
                y = np.linspace(y0,y1,m)
                r = np.linspace(r0,r1,m)
                g = np.linspace(g0,g1,m)
                b = np.linspace(b0,b1,m)
                im.data[np.round(y).astype(np.int), np.round(x).astype(np.int),:] = 0.5 * np.array([r,g,b]).T

        return im

    def _set_subdir(self, subdir):
        self.chip_dir = os.path.join(self.cache_root, 'pvr', 'chips', subdir)
        self.frontalized_dir = os.path.join(self.output_base_dir, 'frontalized', subdir)
        self.meta_dir = os.path.join(self.output_base_dir, 'meta', subdir)
        self.landmarks_dir = os.path.join(self.output_base_dir, 'landmarks', subdir)
        remkdir(self.chip_dir)
        remkdir(self.frontalized_dir)
        remkdir(self.meta_dir)
        remkdir(self.landmarks_dir)

    def _get_chip_base(self, chip_path):
        return os.path.splitext(os.path.basename(chip_path))[0]

    def _get_chip_relative_fnames(self, chip_path, base_dir, *suffixes):
        fname_base = os.path.join(base_dir, self._get_chip_base(chip_path))
        return (fname_base + suffix for suffix in suffixes)

    def _call_exe(self, exe_args):
        quietprint('[janus.Frontalizer] Calling: %s' % exe_args[0], 1)
        quietprint('[janus.Frontalizer] Calling:\n\t%s' % ' '.join(exe_args), 2)
        try:
            cmd_output = subprocess.check_output(exe_args, stderr=STDOUT)
        except CalledProcessError, e:
            print('Warning: ' + exe_args[0] + ' returned ' + str(e.returncode))
            print(e.output)
            print(' '.join(exe_args))

    def __call__(self, im_or_chip_path, *args, **kwargs):
        # preprocess arguments based on type (chip path vs ImageDetection)
        if isinstance(im_or_chip_path, basestring):
            # looks like we got a filename to a chip
            quietprint('[janus.Frontalizer]: chip path __call__(%s, %s, %s)'%(im_or_chip_path, str(args), str(kwargs)), verbosity=1)
            args = (im_or_chip_path,) + args
        else:
            # looks like we got an image that we need to chip first
            quietprint('[janus.Frontalizer]: image __call__(%s, %s, %s)'%(im_or_chip_path, str(args), str(kwargs)), verbosity=1)
            chip = self.chip(im_or_chip_path, *args, **kwargs)
            args = (chip.filename(),)
            kwargs = {"subdir": chip.category() if self.use_category_subdirs else None}
            #kwargs = {}
                #def _chip_path(self, chip_path, subdir=None, finalize_only=False):

        # chip should definitely be ready now, so frontalize if needed
        if self.generate_frontalization == "always" or \
           ( self.generate_frontalization == "as_needed"
             and not self.output_exists(*args, **kwargs)):

            quietprint('[janus.Frontalizer.__call__]: Calling frontalization', 2)
            try:
                result = self._chip_path(*args, **kwargs)
            except Exception as e:
                quietprint('[janus.frontalizer.__call__]: self._chip_path(%s, %s) failed:\n%s'%(str(args), str(kwargs), str(e)), verbosity=0)

        # if an image was passed in, the caller expects a list of the frontalized images as output
        images = []
        try:
            if self.output_exists(*args, **kwargs):
                images = self.get_output_images(im_or_chip_path)
            else:
                quietprint('[janus.Frontalizer.__call__]: Could not find output %s %s'%(str(args), str(kwargs)), 2)
        except Exception as e:
            # it was just a chip path, so just return the result
            quietprint('[janus.frontalizer.__call__]: self.get_output_images(%s) failed:\n%s'%(str(im_or_chip_path), str(e)), verbosity=0)
            return result
        images.append(im_or_chip_path)
        return images

    def _postprocess_camera(self, chip_path):
        camera_fname, pose_fname = self._get_chip_relative_fnames(chip_path, self.meta_dir,
            '_camera.txt', '_pose.csv')

        try:
            P = io_utils.read_matrix(camera_fname)
        except IOError:
            print('error reading camera filename ' + camera_fname)
            raise

        # decompose camera into intrinsic and extrinsic parameters
        _,_,R,_ = camera_decomposition.decompose_affine(P)
        # convert rotation matrix to Euler Angle representation
        pitch, yaw, roll = camera_decomposition.decompose_rotation(R)
        # write out pose parameters as a csv file
        with open(pose_fname,'wb') as pfd:
            writer = csv.DictWriter(pfd,('pitch','yaw','roll'),delimiter=',')
            writer.writeheader()
            writer.writerow({'pitch':pitch, 'yaw':yaw, 'roll':roll})

    def get_chip_path(self, im_path, subdir=None):
        if subdir is not None:
            self._set_subdir(subdir)
        return os.path.join(self.chip_dir, '%s.png'%self._get_chip_base(im_path))

    def chip(self, im, dilate=None, resize_cols=None):
        """
        Chip an image to contain just the cropped bounding box, and saves it to disk.

        If self.generate_frontalization=='never' or 'as_needed' and the image already exists,
        then it is not recomputed.

        Either way, the ImageDetection object is cloned and points to the chip filename,
        unless generate_frontalization=='never' and the chip didn't exist, in which case it
        returns None.

        dilate, if not None, sets the dilation of the bounding box before cropping. This is useful
        for having a tight crop of the face for the input image FV, but a bigger BB for the head
        for Frontalization.

        resize_cols, if not None, is the number of columns to resize to. Note that the new (as of
        2015-07-10 or so, right after the v0.7 release) PVR frontalization doesn't need input
        images to be a specific size anymore. Default used to be 300.
        """
        chip_path = self.get_chip_path(im.filename(), im.category() if self.use_category_subdirs else None)
        quietprint('[janus.Frontalizer.chip] Chipping image %s to chip path %s...'%(str(im), chip_path), verbosity=2)
        chip = im.clone()
        if self.generate_frontalization=='always' or \
          (self.generate_frontalization=='as_needed' and not os.path.isfile(chip_path)):
            # Write chip to file for PVR
            # PVR will resample small images with width < 250
            chip_dir = os.path.dirname(chip_path)
            bobo.util.remkdir(chip_dir)
            if dilate is not None:
                chip = chip.boundingbox(dilate=dilate)
            chip = chip.crop()#.grayscale()
            if resize_cols is not None:
                if resize_cols > 0:
                    chip = chip.resize(cols=resize_cols)
                elif resize_cols < 0:
                    # upsample if chip is too small, but don't downsample if already big
                    if chip.width() < -resize_cols:
                        chip = chip.resize(cols=-resize_cols)
            quietprint('[janus.Frontalizer.chip]: Writing image chip to %s'%chip_path)
            chip.saveas(chip_path)
        elif self.generate_frontalization=='as_needed':
            assert os.path.isfile(chip_path)
            quietprint('[janus.Frontalizer.chip] Chip already existed', verbosity=2)
        else:
            assert self.generate_frontalization == 'never'
            quietprint('[janus.Frontalizer.chip] Never chipping', verbosity=2)

        if os.path.isfile(chip_path):
            return chip.filename(newfile=chip_path)
        else:
            quietprint('[janus.Frontalizer.chip]: Expected %s to be a chip file, but it\'s not. Did we try to generate? %s'%(chip_path, self.generate_frontalization), verbosity=2)
            return None


    def get_output_fnames(self, chip_path, subdir=None):
        raise NotImplementedError('Child classes must implement get_output_fnmaes')

    def output_exists(self, chip_path, subdir=None):
        raise NotImplementedError('Child classes must implement output_exists')

    def check_output(self, chip_path, subdir=None):
        if subdir:
            self._set_subdir(subdir)
        
        # Look for new output
        if not self.output_exists(chip_path):
            print('error checking frontalization output at %s, ...' % 
                self.get_output_fnames(chip_path)[0])
            return False
        return True

class FrontalizerChip(Frontalizer):
    def __init__(self, gpu_idx, cache_root=None,
                target_img_nx=150, target_img_ny=150,
                yawdeg=0, pitchdeg=0, rolldeg=0,
                generate_frontalization="as_needed", use_category_subdirs=False):
        super(FrontalizerChip, self).__init__(gpu_idx=gpu_idx, cache_root=cache_root,
                target_img_nx=target_img_nx, target_img_ny=target_img_ny,
                generate_frontalization=generate_frontalization, use_category_subdirs=use_category_subdirs)

        self.yawdeg = yawdeg
        self.pitchdeg = pitchdeg
        self.rolldeg = rolldeg

        # chip camera dir
        self.target_camera_dir = os.path.join(bobo.app.root(), 'models','pvr','mean_face_whair','render','cameras')
        remkdir(self.target_camera_dir)
        self.target_camera_fname = os.path.join(self.target_camera_dir,
            'mean_face_yaw_+%02d_pitch_+%02d_roll_+%02d_camera.txt' %
            (self.yawdeg, self.pitchdeg, self.rolldeg))
        # TODO: handle frontalized_raw

    def _set_subdir(self, subdir):
        super(FrontalizerChip, self)._set_subdir(subdir)
        self.frontalized_raw_dir = os.path.join(self.output_base_dir, 'frontalized_raw', subdir)
        remkdir(self.frontalized_raw_dir)

    def _chip_path(self, chip_path, subdir=None, finalize_only=False):
        # Janus env.sh should have this on the path
        frontalize_3d_exe = 'frontalize_face'
        finalize_exe = os.path.join(self.pvr_python_dir, 'finalize_frontalization.py')

        # change frontalized subdir?
        if subdir:
            self._set_subdir(subdir)

        """ main """
        # loop over all face chips
        quietprint('frontalizing chip %s' % (chip_path), 2)
        camera_fname, face_params_fname = self._get_chip_relative_fnames(chip_path, self.meta_dir, 
            '_camera.txt', '_face_params.txt')
        # estimate camera parameters
        frontalized_fname, frontalized_fg_mask_fname, frontalized_vis_mask_fname, frontalized_og_mask_fname = \
            self._get_chip_relative_fnames(chip_path, self.frontalized_raw_dir,
                '_frontalized_raw.png', '_fg_mask.png', '_vis_mask.png', '_og_mask.png')

        if not finalize_only:
            frontalize_args = (frontalize_3d_exe,
                               chip_path,
                               self.target_camera_fname, str(self.target_img_nx), str(self.target_img_ny),
                               self.source_pvr_model, self.target_pvr_model,
                               frontalized_fname, frontalized_fg_mask_fname, frontalized_vis_mask_fname, frontalized_og_mask_fname,
                               camera_fname, face_params_fname, self.gpu_idx, self.landmark_model_dir)

            self._call_exe(frontalize_args)
            self._postprocess_camera(chip_path)

        if not os.path.exists(frontalized_fname):
            print('error reading frontalized filename ' + frontalized_fname)
            return

        frontalized_wsym_fname, frontalized_mask_fname = self._get_chip_relative_fnames(chip_path, self.frontalized_dir,
            '_frontalized_wsym.png', '_frontalized_mask.png')
        finalize_args = (finalize_exe,
                     frontalized_fname, frontalized_fg_mask_fname, frontalized_vis_mask_fname,
                     chip_path, camera_fname, self.target_camera_fname,
                     frontalized_wsym_fname, frontalized_mask_fname)
        self._call_exe(finalize_args)

        return self.check_output(chip_path)

    def get_output_fname(self, chip_path, subdir=None):
        if subdir:
            self._set_subdir(subdir)

        frontalized_wsym_fname, = self._get_chip_relative_fnames(chip_path, self.frontalized_dir,
            '_frontalized_wsym.png')

        return frontalized_wsym_fname

    def get_output_fnames(self, chip_path, subdir=None):
        return [self.get_output_fname(chip_path, subdir=subdir)]

    def output_exists(self, chip_path, subdir=None):
        expected_fname = self.get_output_fname(chip_path, subdir=subdir)
        print '------------test'
        print expected_fname
        
        
        return os.path.isfile(expected_fname)

class FrontalizerFaceV5(Frontalizer):
    def __init__(self, gpu_idx, cache_root=None,
                target_img_nx=150, target_img_ny=150, model_subdir='.',
                render_yaw_vals=[-40,0,40], render_pitch_vals=[-30,0,30],
                use_view_dep_apm=False, paint_with_mirror_images=False,
                use_surface_normals=False, input_scale_factor=2,
                generate_frontalization="as_needed", use_category_subdirs=False):
        super(FrontalizerFaceV5, self).__init__(gpu_idx=gpu_idx, cache_root=cache_root,
                target_img_nx=target_img_nx, target_img_ny=target_img_ny, model_subdir=model_subdir,
                generate_frontalization=generate_frontalization, use_category_subdirs=use_category_subdirs)

        self.render_yaw_vals = render_yaw_vals
        self.render_pitch_vals = render_pitch_vals
        self.use_view_dep_apm = use_view_dep_apm
        self.paint_with_mirror_images = paint_with_mirror_images
        self.use_surface_normals = use_surface_normals
        self.input_scale_factor = input_scale_factor

        # face_v5 camera dir
        self.render_cam_dir = os.path.join(self.cache_root, 'pvr', 'render_cams')
        remkdir(self.render_cam_dir)

        # generate cameras for synthetic renderings
        self.render_cam_fnames = []
        self.render_fsuffixes = [fsuffix for (_,_,fsuffix) in self._yp_fsuffix()]
        from janus.pvr import generate_blender_camera  # HACK: import at runtime        
        try:
            for yaw,pitch,render_fsuffix in self._yp_fsuffix():
                P = generate_blender_camera.generate_blender_camera(yaw, pitch, 0, img_shape=(self.target_img_nx, self.target_img_ny))
                camera_fname = os.path.join(self.render_cam_dir, render_fsuffix+'.txt')
                self.render_cam_fnames.append(camera_fname)
                io_utils.write_matrix(P, camera_fname)
        except:
            # Probably no PVR, ignore and move on
            raise

    def _yp_fsuffix(self):
        for yaw in self.render_yaw_vals:
            for pitch in self.render_pitch_vals:
                yield yaw, pitch, 'yaw_%+03d_pitch_%+03d' % (yaw,pitch)

    def _chip_path(self, chip_path, subdir=None):
        # Janus env.sh should have this on the path
        render_face_exe = 'render_face'

        # change frontalized subdir?
        if subdir:
            self._set_subdir(subdir)

        """ main """
        quietprint('[janus.frontalize.FrontalizerFaceV5._chip_path] frontalizing chip %s' % (chip_path), 2)
        frontalize_args = [render_face_exe,
                           "--input_images", chip_path,
                           "--base_model", self.source_pvr_model,
                           "--target_model", self.target_pvr_model,
                           "--output_image_dir", self.frontalized_dir,
                           "--output_meta_dir", self.meta_dir,
                           "--gpu_idx", self.gpu_idx,
                           "--input_face_min_width", str(self.input_scale_factor*self.target_img_nx), # input pixels >> model voxels
                           "--input_face_max_width", str(self.input_scale_factor*self.target_img_nx), # input pixels >> model voxels
                           "--view_dep_apm", str(int(self.use_view_dep_apm)),
                           "--paint_with_mirror_images", str(int(self.paint_with_mirror_images)),
                           "--use_surface_normals",str(int(self.use_surface_normals)),
                           "--output_width", str(self.target_img_nx),
                           "--output_height", str(self.target_img_ny),
                           "--landmark_model_dir", self.landmark_model_dir]
        if len(self.render_cam_fnames) > 0:
            frontalize_args.append("--output_cameras")
            frontalize_args.extend(self.render_cam_fnames)

        self._call_exe(frontalize_args)
        self._postprocess_camera(chip_path)
        
        return self.check_output(chip_path)

    def get_output_fnames(self, chip_path, subdir=None):
        if subdir:
            self._set_subdir(subdir)

        chip_base, = self._get_chip_relative_fnames(chip_path, self.frontalized_dir, '_')
        return sorted([chip_base + suffix + '_frontalized.png' for suffix in self.render_fsuffixes])

    def get_output_images(self, chip, subdir=None):
        if subdir:
            self._set_subdir(subdir)
        if isinstance(chip, basestring):
            return [Image().filename(newfile=fname) for fname in self.get_output_fnames(chip)]
        else:
            return [chip.clone().filename(newfile=fname) for fname in self.get_output_fnames(chip.filename())]

    def output_exists(self, chip_path, subdir=None):
        expected_fnames = self.get_output_fnames(chip_path, subdir=subdir)
        return all(map(os.path.isfile, expected_fnames))

        # # Look for output
        # glob_spec, = self._get_chip_relative_fnames(chip_path, self.frontalized_dir,
        #     '*_frontalized.png')
        # globbed_fnames = glob.glob(glob_spec)
        # return set(expected_fnames) <= set(globbed_fnames)

def init_pvr_model(gpu_idx):
    """ Initialize the PVR mean face model from a point cloud """
    # Keep imports here to support PVR-less builds
    try:
        import io_utils
        from janus.pvr import camera_decomposition
        from janus.pvr import PVR_from_point_cloud
        from janus.pvr import paint_PVR_model
        from janus.pvr import generate_blender_camera
    except ImportError, e:
        pass

    smooth_model_exe = 'filter-model'
    pvr_python_dir = bobo.app.release() +  '/janus/pvr'
    pvr_from_point_cloud_exe = pvr_python_dir + '/PVR_from_point_cloud.py'
    refine_its = 1

    ply_filename = bobo.app.root() + '/models/pvr/mean_face_whair/mesh/mean_face_whair_cloud.ply'

    cache_root = bobo.app.janusCache()

    #### NOTE: The below model dirs will be completely overwritten!!
    model_dir = cache_root + '/models/pvr/mean_face'
    target_model_dir = cache_root + '/models/pvr/target_face'

    remkdir(model_dir)
    remkdir(target_model_dir)
    ####

    image_form = bobo.app.root() + '/models/pvr/mean_face_whair/render/images/mean_face_yaw_%+03d_pitch_%+03d_roll_%+03d.png'
    camera_form = bobo.app.root() + '/models/pvr/mean_face_whair/render/cameras/mean_face_yaw_%+03d_pitch_%+03d_roll_%+03d_camera.txt'

    num_blocks = (1,1,1)
    max_num_subblocks = 300

    #apm_model_str = 'boxm2_gauss_rgb'
    apm_model_list = ('boxm2_mog3_grey', 'boxm2_num_obs', 'boxm2_mog3_grey_frontalized', 'boxm2_num_obs_frontalized')

    do_init = True
    if do_init:
        init_args = ['python', pvr_from_point_cloud_exe, ply_filename, '--model_dir', model_dir, '--num_blocks', str(num_blocks[0]), str(num_blocks[1]), str(num_blocks[2]), '--max_num_subblocks', str(max_num_subblocks), '--appearance_models']
        for apm_str in apm_model_list:
            init_args.append(apm_str)
        init_args.extend(['--refine_its',str(refine_its)])

        retcode = subprocess.call(init_args)
        if not retcode == 0:
            print(pvr_from_point_cloud_exe + ' returned error: ' + str(retcode))
            #exit(-1)
        print('Done.')

    model_xml_path = model_dir + '/scene.xml'

    # smooth the geometry
    smooth_its = 6
    print('Smoothing Geometry..')
    if smooth_its > 0:
        smooth_args = (smooth_model_exe, model_xml_path, str(smooth_its), str(gpu_idx))
        retcode = subprocess.call(smooth_args)
        if not retcode == 0:
            print(smooth_model_exe + ' returned error: ' + str(retcode))
            #exit(-1)
        print('Done.')

    # paint the model with rendered images
    image_filenames = []
    camera_filenames = []
    for yaw in range(-90, 91, 10):
        for pitch in range(-90, 91, 10):
            for roll in (0,):
                image_filenames.append( image_form % (yaw,pitch,roll) )
                camera_filenames.append( camera_form % (yaw,pitch,roll) )

    paint_PVR_model.paint_PVR_model(model_xml_path, image_filenames, camera_filenames)

    # copy the model to the target dir
    shutil.rmtree(target_model_dir,ignore_errors=True)
    shutil.copytree(model_dir, target_model_dir)



def frontalize_chip(chip_path, gpu_idx, cache_root=None, yawdeg=0, pitchdeg=0, rolldeg=0, target_img_nx=150, target_img_ny=150, subdir=None):
    """ estimate camera parameters for CS0 face chips """
    f = FrontalizerChip(gpu_idx=gpu_idx, cache_root=cache_root,
                        target_img_nx=target_img_nx, target_img_ny=target_img_ny,
                        yawdeg=yawdeg, pitchdeg=pitchdeg, rolldeg=rolldeg)
    f(chip_path, subdir=subdir)


def frontalize_face_v5(chip_path, gpu_idx, cache_root=None, render_yaw_vals=[-40,0,40], render_pitch_vals=[-30,0,30], target_img_nx=150, target_img_ny=150, subdir=None):
    """ estimate camera parameters for CS0 face chips """
    f = FrontalizerFaceV5(gpu_idx=gpu_idx, cache_root=cache_root, use_surface_normals=True,
                        target_img_nx=target_img_nx, target_img_ny=target_img_ny,
                        render_yaw_vals=render_yaw_vals, render_pitch_vals=render_pitch_vals, model_subdir=subdir)
    f(chip_path, subdir=subdir)


def relight(im, yaw, pitch, gpu_idx=0, outdir=tempfile.tempdir):
    """Adapted from components/pvr/scripts/relight_CS2.py"""

    # Input chip
    im = im.boundingbox(dilate=1.5).crop().saveas(temppng())

    # Options    
    source_pvr_model = os.path.join(bobo.app.models(), 'pvr', '20150707', 'mean_face', 'scene.xml')
    target_pvr_model = os.path.join(bobo.app.models(), 'pvr', '20150707', 'target_face',  'scene.xml')
    output_dir = outdir
    input_face_min_width = 300
    input_face_max_width = 300
    use_surface_normals = True
    input_upsample_factor = 1
    use_alfw_landmarks = False
    viewer_centric_light_dirs = True
    landmark_model_dir = None
    debug_dir = None
    chip_path = im.filename()
    
    # Executable
    light_R_fnames = []
    R_light = geometry_utils.Euler_angles_to_matrix((np.deg2rad(yaw), np.deg2rad(pitch), 0), order=(1,0,2))
    light_dir = -R_light[:,2]  # that is, R_light * [0,0,-1]
    light_fname = os.path.join(tempfile.tempdir, 'yaw_%+03d_pitch_%+03d.txt' % (yaw,pitch))
    light_R_fnames.append(light_fname)
    io_utils.write_matrix(light_dir, light_fname)
        
    relight_args = ['render_face_relit',  # already on path
                        "--input_image", chip_path,
                        "--base_model", source_pvr_model,
                        "--target_model", target_pvr_model,
                        "--output_directory", output_dir,
                        "--gpu_idx", str(gpu_idx),
                        "--input_face_min_width", str(input_face_min_width),
                        "--input_face_max_width", str(input_face_max_width),
                        "--use_surface_normals",str(int(use_surface_normals)),
                        "--use_alfw_landmarks", str(int(use_alfw_landmarks)),
                        "--input_upsample_factor", str(input_upsample_factor),
                        "--viewer_centric", str(int(viewer_centric_light_dirs))]
    relight_args.append('--light_directions')
    relight_args.extend(light_R_fnames)

    if landmark_model_dir is not None:
        relight_args.extend(['--landmark_model_dir',landmark_model_dir])

    if debug_dir is not None:
        relight_args.extend(['--debug_dir', debug_dir])
        
    print(' '.join(relight_args))
    retcode = subprocess.call(relight_args, stdout=open(os.devnull, 'w'))

    if retcode != 0:
        print('Warning: ' + relight_args[0] + ' returned ' + str(retcode))
        print(' '.join(relight_args))
    else:
        return im.clone().flush().filename(os.path.join(output_dir, '%s_%s.png' % (filebase(im.filename()), filebase(light_R_fnames[0]))))
        
    
    
