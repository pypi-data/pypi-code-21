import numpy as np
import tempfile
import os
import sys
import subprocess
import shutil
from itertools import product

# FIXME: bobo.util import raises scipy.io import error
def remkdir(path, flush=False):
    """Create a given directory if not already exists"""
    if os.path.isdir(path) is False:
        os.makedirs(path)
    elif flush == True:
        shutil.rmtree(path)
        os.makedirs(path)
    return path


def writetemplate(T, mtxfile=None):
    """Write an STR Janus Phase II template to a binary file in a format similar
    to NIST BEE matrices"""

    """ Expected inputs:
        Tuple of (template role, final encoding, svm weights, media encodings)

        All  32-bit floating data arrays are in row-major order.
        - template role: int32_t
        - final encoding rows (either 0 or 1): int32_t
        - final encoding cols (varies, will be 0 if rows is 0): int32_t
        - final encoding (rows*cols): float32 * rows * cols
        - svm weights rows (either 0 or 1): int32_t
        - svm weights cols (varies, will be 0 if rows is 0): int32_t
        - svm weights (rows*cols+1, last value is bias term): float32
        - media encodings rows: int32_t
        - media encodings cols: int32_t
        - media encodings (rows*cols): float32
        """
    def _writemtx(mtx, f):
        (row, col) = mtx.shape
        f.write(np.array([row], dtype=np.uint32).view(np.uint8).tostring())
        f.write(np.array([col], dtype=np.uint32).view(np.uint8).tostring())
        f.write(mtx.view(np.uint8).tostring())  # see also ndarray.tofile

    mtxfile = tempfile.mktemp() + '.mtx' if mtxfile is None else mtxfile
    (role, fenc, svm, media) = T
    with open(mtxfile, 'wb') as f:
        f.write(np.array( [role], dtype=np.uint32).view(np.uint8).tostring())
        _writemtx(fenc, f)
        _writemtx(svm, f)
        _writemtx(media, f)
        return mtxfile


def readtemplate(mtxfile):
    """Reads STR Janus Phase II template from  a binary file """
    """ Expected format:
        All  32-bit floating data arrays are in row-major order.
        - template role: int32_t
        - final encoding rows (either 0 or 1): int32_t
        - final encoding cols (varies, will be 0 if rows is 0): int32_t
        - final encoding (rows*cols): float32 * rows * cols
        - svm weights rows (either 0 or 1): int32_t
        - svm weights cols (varies, will be 0 if rows is 0): int32_t
        - svm weights (rows*cols+1, last value is bias term): float32
        - media encodings rows: int32_t
        - media encodings cols: int32_t
        - media encodings (rows*cols): float32
        """

    def _readmtx(f, idx):
        rows = int(np.fromfile(f, dtype=np.uint32, count=1, sep=''))
        idx += 4; f.seek(idx)
        print 'rows: % d' % rows

        cols = int(np.fromfile(f, dtype=np.uint32, count=1, sep=''))
        idx += 4; f.seek(idx)
        print 'cols: % d' % cols

        mtx = np.reshape(np.fromfile(f, dtype=np.float32,
                                     count=rows*cols, sep=''), (rows, cols))
        idx += 4 * rows * cols
        return mtx, idx

    with open(mtxfile, 'rb') as f:
        idx = 0
        role = int(np.fromfile(f, dtype=np.uint32, count=1, sep=''))
        idx += 4; f.seek(idx)
        print 'role: %d' % role

        print 'final encoding:'
        final_encoding, idx = _readmtx(f, idx)
        print 'svm weights:'
        svm_weights, idx = _readmtx(f, idx)
        print 'encodings'
        encodings, idx = _readmtx(f, idx)

        return (role, final_encoding, svm_weights, encodings)


class D30TNERecognition(object):
    """Allows gallery enrollment and search, and
    reference and probe template encoding and verification
    using the Janus test harness executables.
    NOTE: Expects janus test harness executables to be on the system path"""

    """ Init """
    def __init__(self, sdk_path, data_path, output_path,
                 trainset=None,
                 dlib_dnn_model=None,
                 dlib_num_features=None,
                 gpu_index=0, verbose=False):

        self.sdk_path = sdk_path

        self.launch_script = os.path.join(self.sdk_path, 'scripts', 'launch_tne_exe.sh')
        # print self.launch_script

        self.output_path = output_path
        self.data_path = data_path
        self.gpu_index = gpu_index
        self.verbose = verbose
        self.dlib_dnn_model = dlib_dnn_model if dlib_dnn_model is not None else 'config/models/dlib_dnn/vggface_logspace_05JUN16.dlib'
        self.trainset = trainset if trainset is not None else 'config/models/negativeset_24AUG16/str_broadface_vggface_05JUN16.mtx'
        self.dlib_num_features = dlib_num_features if dlib_num_features is not None else 4096

        # Sanity check
        res = subprocess.call(['bash', '-c', 'type %s &> /dev/null; exit $?' % self.launch_script], shell=False)
        if res != 0:
            raise RuntimeError('[D30TNERecognition]: Could not find Janus test'
                    ' harness launch script at "%s"' % self.launch_script)


    """ Util """
    def _config(self):
        return (' --use_dlib_encoder=True'
                ' --dlib_dnn_model=%s'
                ' --dlib_dnn_num_features=%s'
                ' --face_detector_type=rcnn'
                ' --rcnn_caffemodel_filename=config/models/faster_rcnn/vgg16_faster_rcnn_wider_fine_tune_reg_wider_dets_from_cs3_5000_ims_iter_15000.caffemodel'
                ' --rcnn_prototxt_filename=config/models/faster_rcnn/test.prototxt'
                ' --encode_batch_size=20'
                ' --debug=False'
                ' --debug_images=False'
                ' --trainset_filename=%s'
                ' --boundingbox_scale=1.1'
                ' --do_gallery_adaptation=True'
                ' --use_gallery_negatives=True'
                ' --gallery_negatives_only=False'
                ' --do_probe_adaptation=True'
                ' --svm_c=10'
                ' --svm_threads=8'
                 % (self.dlib_dnn_model, str(self.dlib_num_features), self.trainset)
                )


    def _algorithm(self):
        config_file = tempfile.mktemp()
        with open(config_file, 'w'):
            # Create empty file
            pass

        algorithm = '--config=%s %s' % (config_file, self._config())
        return algorithm


    def _template_subdir(self, template_role):
        # ENROLLMENT_11 = 0,
        # VERIFICATION_11 = 1,
        # ENROLLMENT_1N = 2,
        # IDENTIFICATION = 3,
        # CLUSTERING = 4
        if template_role == 0:
            return 'verification/reference'
        elif template_role == 1:
            return 'verification/probe'
        elif template_role == 2:
            return 'search/probe'
        elif template_role == 3:
            return 'search/template'
        elif template_role == 4:
            return 'clustering/template'
        else:
            raise RuntimeError('Unsupported template role: %s'
                               % str(template_role))


    def _gallery_path(self):
        gallery_path = os.path.join(self.output_path, 'search', 'gallery')
        return gallery_path


    def _templates_from_file(self, template_list_file):
        templates = {}
        with open(template_list_file, 'r') as f:
            for l in f:
                p = l.strip().split(',')
                templates[p[0]] = p
        return templates


    def _verification_list_files(self, reference_list_file, probe_list_file):
        reference_templates = self._templates_from_file(reference_list_file)
        probe_templates = self._templates_from_file(probe_list_file)

        list_file_path = os.path.join(self.output_path, 'verification')
        template_list_file_a = os.path.join(list_file_path, 'reference_list_file.csv')
        template_list_file_b = os.path.join(list_file_path, 'probe_list_file.csv')

        template_pairs = product(reference_templates, probe_templates)
        with open(template_list_file_a, 'w') as af, open(template_list_file_b, 'w') as bf:
            for p,q in template_pairs:
                a = reference_templates[p]
                af.write('%s\n'%','.join(a))
                b = probe_templates[q]
                bf.write('%s\n'%','.join(b))

        return (template_list_file_a, template_list_file_b)


    def _try_command(self, cmd):
        full_cmd = [self.launch_script] + cmd
        full_cmd += ['-algorithm', '%s' % self._algorithm()]

        if self.verbose:
            full_cmd += '-verbose'
        # print 'full_cmd: [\n%s\n]' % '\n'.join(full_cmd)

        try:
            res = subprocess.call(full_cmd, shell=False)

        except:
            print '[D30TNERecognition]: Execption while running'
            print '%s' % ('\n'.join(full_cmd))
            raise

        if res != 0:
            raise RuntimeError('command returned %d:\n%s' %
                    (res, '\n'.join(full_cmd)))


    """ Exe commands """
    def _create_templates(self, metadata, templates_path, template_role):
        """ Runs janus_create_templates to encode gallery, probe, reference, or
        verification templates """

        """ janus_create_templates
        $sdk_path
        $temp_path
        $data_path
        $metadata
        $templates_path
        $templates_list_file
        $template_role
        -gpuindex $gpu_index
        -algorithm --config=$config_file
        -verbose
        """

        templates_list_file = os.path.join(templates_path, 'templates.csv')
        config_file = tempfile.mktemp()
        with open(config_file, 'w'):
            # Create empty file
            pass

        cmd = [ 'janus_create_templates',
                self.sdk_path,
                self.output_path,
                self.data_path,
                metadata,
                templates_path+'/',
                templates_list_file,
                str(template_role),
                '-gpuindex', str(self.gpu_index),
                ]

        self._try_command(cmd)
        return templates_list_file


    def _create_gallery(self, gallery_list_file):
        gallery_path = self._gallery_path()
        remkdir(gallery_path)
        gallery_file = os.path.join(gallery_path, 'g.gallery')

        """
            janus_create_gallery
            $sdk_path
            $temp_path
            $templates_list_file
            $gallery_file
            -algorithm --config=$config_file
        """

        cmd = [ 'janus_create_gallery',
                self.sdk_path,
                self.output_path,
                gallery_list_file,
                gallery_file,
                '-algorithm', self._algorithm(),
                ]
        self._try_command(cmd)
        return gallery_file


    def _search(self, probe_list_file, gallery_list_file, gallery_file, num_req_returns):

        """ janus_search
            sdk_path
            temp_path
            probes_list_file
            gallery_list_file
            gallery_file
            num_req_returns
            candidate_list_file
            [-algorithm
            <algorithm>]
            [-verbose]
        """
        cand_list_path = os.path.join(self.output_path, 'search', 'candlists')
        remkdir(cand_list_path)
        cand_list_file = os.path.join(cand_list_path, 's.candidate_lists')
        cmd = [ 'janus_search',
                self.sdk_path,
                self.output_path,
                probe_list_file,
                gallery_list_file,
                gallery_file,
                str(num_req_returns),
                cand_list_file,
                '-algorithm', self._algorithm(),
               ]
        self._try_command(cmd)
        return cand_list_file


    def _verify(self, reference_list_file, probe_list_file):
        """ janus_verify
            sdk_path
            temp_path
            templates_list_file_a
            templates_list_file_b
            scores_file
            [-algorithm <algorithm>]
            [-verbose]
        """

        scores_path = os.path.join(self.output_path, 'verfication', 'scores')
        remkdir(scores_path)
        scores_file = os.path.join(scores_path, 'verify.scores')

        cmd = [ 'janus_verify',
                self.sdk_path,
                self.output_path,
                reference_list_file,
                probe_list_file,
                scores_file,
                '-algorithm', self._algorithm(),
               ]
        self._try_command(cmd)
        return scores_file


    """ User commands """
    def create_templates(self, metadata, template_role):
        """Creates templates from metadata and returns a template list file.
        metdata is a csv file in the CS3 protocol format.  template_role
        describes what the template will be used for.  Supported roles are:
        # ENROLLMENT_11 = 0,   # Reference 1v1
        # VERIFICATION_11 = 1, # Probe 1v1
        # ENROLLMENT_1N = 2,   # Gallery 1vN
        # IDENTIFICATION = 3,  # Probe 1vN
        # CLUSTERING = 4
        """
        if not os.path.isfile(metadata):
            raise RuntimeError('[D30TNERecognition.create_template]: Invalid metadata file: %s' % metadata)

        t_subdir = self._template_subdir(template_role)
        templates_path = os.path.join(self.output_path, t_subdir)
        remkdir(templates_path)
        return self._create_templates(metadata, templates_path, template_role)


    def create_gallery(self, metadata):
        """
        Returns a gallery file with the templates from the list file enrolled.
        metadata is a csv file in the CS3 protocol format.
        """
        template_role = 3
        gallery_list_file = self.create_templates(metadata, template_role)
        return self._create_gallery(gallery_list_file)


    def create_gallery_from_templates(self, template_list_file):
        """
        Returns a gallery file with the templates from the list file enrolled.
        template_list_file is a csv file from a call to create_templates with
        a template_role of 2 (ENROLLMENT_1N).
        """
        return self._create_gallery(template_list_file)


    def search(self, gallery_metadata, probe_metadata, num_req_returns):
        """
        Returns a candate list file containing num_req_return match scores
        against the gallery for each probe.  gallery_metadata and probe_metadata
        are csv files in the CS3 protocol format.
        """
        gallery_template_role = 2
        gallery_list_file = self.create_templates(gallery_metadata, gallery_template_role)

        gallery_file = self._create_gallery(gallery_list_file)

        probe_template_role = 3
        probe_list_file = self.create_templates(probe_metadata, probe_template_role)

        return self._search(probe_list_file, gallery_list_file, gallery_file, num_req_returns)


    def search_gallery_probe(self, gallery_file, gallery_list_file, probe_list_file, num_req_returns):
        """
        Returns a candate list file containing num_req_return match scores
        against the gallery for each probe.  gallery_file is a file returned
        by create_gallery() or create_gallery_from_templates(),
        gallery_list_file and probe_list file are csv files returned by
        create_templates().
        """
        return self._search(probe_list_file, gallery_list_file, gallery_file, num_req_returns)


    def verify(self, reference_metadata, probe_metadata):
        """
        Returns a file containing the pairwise scores for cartesian product
        of the templates the reference and probe list. reference_metadata and
        probe_metadata are csv files in the CS3 protocol format.
        """

        reference_role = 0
        reference_list_file = self.create_templates(reference_metadata, reference_role)

        probe_role = 1
        probe_list_file = self.create_templates(probe_metadata, probe_role)

        template_list_file_a, template_list_file_b = self._verification_list_files(reference_list_file, probe_list_file)
        return self._verify(template_list_file_a, template_list_file_b)


    def verify_templates(self, reference_list_file, probe_list_file):
        """
        Returns a file containing the pairwise scores for cartesian product
        of the templates the reference and probe list. reference_list_file and
        probe_list_file are csv files returned by create_templates()
        """
        template_list_file_a, template_list_file_b = self._verification_list_files(reference_list_file, probe_list_file)
        return self._verify(template_list_file_a, template_list_file_b)
