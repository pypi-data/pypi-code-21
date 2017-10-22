import numpy as np
import scipy
import menpo.io as mio
import functools
import time
import traceback

from menpo.image import Image
from menpo.shape import PointCloud
# deep modules
import deepmachine

from .. import utils
from .. import losses
from .. import summary
from .. import data_provider
from .. import ops
from .. import networks
from ..flags import FLAGS



def get_densereg_pose(n_classes=26, use_regression=True):
    # create machine
    model = deepmachine.DeepMachine(
        network_op=functools.partial(
            networks.pose.DenseRegPose,
            n_classes=n_classes,
            deconv='transpose+conv+relu',
            bottleneck='bottleneck_inception'
        )
    )

    # add losses
    model.add_loss_op(losses.loss_iuv_regression)

    # add summaries
    model.add_summary_op(summary.summary_iuv)

    return model


def get_densereg_face(n_classes=11, use_regression=False):
    # create machine
    model = deepmachine.DeepMachine(
        network_op=functools.partial(
            networks.face.DenseRegFace,
            n_classes=FLAGS.quantization_step + 1,
            deconv='transpose+conv'
        )
    )

    # add losses
    model.add_loss_op(losses.loss_uv_classification)

    # add summaries
    model.add_summary_op(summary.summary_uv)

    return model
