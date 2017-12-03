import math
import sys

import torch
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


def repackage_hidden(h):
    """
    Wraps hidden states in new Variables, to detach them from their history.
    """
    if type(h) == Variable:
        return Variable(h.data)
    else:
        return tuple(repackage_hidden(v) for v in h)


def sort_batch(lengths, others):
    """
    Sort batch data and labels by length.
    Useful for variable length inputs, for utilizing PackedSequences
    Args:
        lengths (nn.Tensor): tensor containing the lengths for the data
        others (iterable): training data or labels to sort according to lengths

    Returns:

    """
    batch_size = lengths.size(0)

    sorted_lengths, sorted_idx = lengths.sort()
    reverse_idx = torch.linspace(batch_size - 1, 0, batch_size).long()
    sorted_lengths = sorted_lengths[reverse_idx]

    return sorted_lengths, (lst[sorted_idx][reverse_idx] for lst in others)


def packed_targets(targets, lengths):
    """
    pack and unpack (pad) targets,
    in order to make them 1-to-1 with the outputs.
    this is needed for NLG.
    Args:
        targets (): sequence of targets
        lengths ():

    Returns:

    """
    targets = pack_padded_sequence(targets, list(lengths.data),
                                   batch_first=True)
    targets, lengths = pad_packed_sequence(targets, batch_first=True)
    return targets, lengths


def epoch_progress(loss, epoch, batch, batch_size,
                   dataset_size, interval=1, ppl=False):
    """
    Print the progress of the training for
    Args:
        loss (float): the average loss for the epoch
        epoch (int): the epoch
        batch (int): the batch
        batch_size (int): the batch size
        dataset_size (int): the training examples in the dataset
        interval (int): how often to update the progress
        ppl (bool): show the average perplexity of the model -> exp(loss)

    Returns:

    """
    batches = math.ceil(float(dataset_size) / batch_size)

    # if interval == 0, then use a sane default
    if interval == 0:
        interval = min([50, math.ceil(batches / 10)])

    if batch % interval != 0 and batch != batches:
        return

    count = batch * batch_size
    bar_len = 40
    filled_len = int(round(bar_len * count / float(dataset_size)))

    log_bar = '=' * filled_len + '-' * (bar_len - filled_len)

    log_losses = ' CE: {:.4f}'.format(loss)

    if ppl:
        log_losses += ', PPL: {:.4f}'.format(math.exp(loss))

    log_epoch = ' Epoch {}'.format(epoch)
    log_batches = ' Batch {}/{}'.format(batch, batches)
    _progress_str = "\r \r {} [{}] {} ... {}".format(log_epoch,
                                                     log_bar,
                                                     log_batches,
                                                     log_losses)
    sys.stdout.write(_progress_str)
    sys.stdout.flush()

    if batch == batches:
        print()


def epoch_summary_lm(dataset, loss, ppl=False):
    msg = "\t{:7s}: Avg Loss = {:.4f}".format(dataset, loss)

    if ppl:
        msg += ',\tAvg Perplexity = {:.4f}'.format(math.exp(loss))

    print(msg)


def save_model_params(model, path):
    """
    Saves only the model params. This is preferred because,
    the serialized data is bound to the specific classes
    and the exact directory structure used,
    so it can break in various ways when used in other projects,
    or after some serious refactoring
    Args:
        model (): a pytorch model
        path (): the path for saving the model params

    Returns:

    """
    torch.save(model.state_dict(), path)


def load_model_params(model, path):
    """
    Load the params (weights) for a given model
    Args:
        model (): the class of the model
        path (): the path of the saved params

    Returns: model

    """
    model.load_state_dict(torch.load(path))
