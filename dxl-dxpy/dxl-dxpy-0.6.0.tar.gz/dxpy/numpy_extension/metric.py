import numpy as np

def psnr(target, label, max_value=None, tor=1e-7):
    shape_check(target, label)
    if max_value is None:
        max_value = np.max([target, label])
    err_square = np.square(target - label)
    err_sum = np.sum(err_square, axis=(1, 2, 3))
    err_sum[err_sum < tor] = tor
    psnr_value = 10.0 * (1.0 + np.log(np.prod(target.shape[1:]) * max_value * max_value / err_sum))
    return psnr_value
