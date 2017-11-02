from bobo.util import readcsv, load, saveas
import matplotlib.pyplot as plt
from bobo.show import savefig
import numpy as np
import os

def plot_log(logfile, minibatchsize, datasetsize, save_dir=None, startepoch=0,rate=50):
    R = readcsv(logfile, separator=' ')

    [log_name, ext] = os.path.splitext(os.path.basename(logfile))
    import pdb
    loss = [float(r[24]) for r in R if len(r) == 43 or len(r) == 32]
    epochs = np.array(range(startepoch,startepoch + rate*len(loss),rate)).astype(np.float32)*(float(minibatchsize)/float(datasetsize))
    plt.figure(1)
    plt.plot(epochs, loss)
    plt.xlabel('Epochs')
    plt.ylabel('Mean Loss')
    plt.grid(True)
    plt.hold(True)
#    pdb.set_trace()


    if save_dir is not None:
        figpath = os.path.join(save_dir, log_name + "_MLoss_vs_Epoch.png")
        plt.savefig(figpath)


    plt.figure(4)
    iterations = rate*np.array(range(0,len(loss)))
    plt.plot(iterations, loss)
    plt.xlabel('Iterations')
    plt.ylabel('Mean Loss')
    plt.grid(True)
    plt.hold(True)
    if save_dir is not None:
        figpath = os.path.join(save_dir, log_name + "_MLoss_vs_it.png")
        plt.savefig(figpath)

    plt.figure(3)
    wallclock = [24.0*(float(r[2][0:2]) + float(r[2][3:5])/24.0 + float(r[2][6:8])/(24.0*60.0))  for r in R if len(r) == 43 or len(r) == 32]
    plt.plot(wallclock, loss)
    plt.xlabel('Wall Clock (hours)')
    plt.ylabel('Mean Loss')
    plt.grid(True)
    plt.hold(True)
    if save_dir is not None:
        figpath = os.path.join(save_dir, log_name + "_MLoss_vs_h.png")
        plt.savefig(figpath)


    plt.figure(2)
    mca = [float(r[31]) for r in R if len(r) == 43 or len(r) == 32]
    plt.plot(epochs, mca)
    plt.xlabel('Epochs')
    plt.ylabel('Mean Classification Accuracy')
    plt.grid(True)
    plt.hold(True)
    if save_dir is not None:
        figpath = os.path.join(save_dir, log_name + "_MCA_vs_Epoch.png")
        plt.savefig(figpath)


if __name__ == '__main__':
    save_dir = '/proj/janus/platform/results/cs4/plots/21SEP17'
    save_dir = None
#    plot_log('/proj/janus/platform/models/dlib-dnn/resnet101_msceleb1m_25JUL17.log', 24*8, 24*8*43741)
#    plot_log('/proj/janus/platform/models/dlib-dnn/resnet101_msceleb1m_14APR17_partial.log', 21*8, 24*8*49991,startepoch =8, rate=500)
    plot_log('/proj/janus/platform/models/dlib-dnn/resnet101_msceleb1m_28AUG17.log', 24*8, 24*8*43741, save_dir=save_dir)
    plot_log('/proj/janus/platform/models/dlib-dnn/resnet101_msceleb1m_21SEP17.log', 21*8, 21*8*49990, save_dir=save_dir)
#    plot_log('/proj/janus/platform/models/dlib-dnn/resnet50_msceleb1m_18AUG17.log', 24*8, 24*8*43741)
#    plot_log('/proj/janus/platform/models/dlib-dnn/resnet50_msceleb1m_22AUG17.log', 24*8, 24*8*43741)
#    plot_log('/proj/janus/platform/models/dlib-dnn/vggVD_vggface_pose_jitter_dual_warped_background_13SEP16.log', 32*4, 32 * 4 * 28482)


#    plot_log('/proj/janus/platform/models/dlib-dnn/resnet101_msceleb1m_14APR17.dlib.log', 21*8, 21*8*49991)
#    plot_log('/proj/janus/platform/models/dlib-dnn/vggVD_vggface_pose_jitter_dual_warped_background_13SEP16.log', 16*4, 16*4*28482)
