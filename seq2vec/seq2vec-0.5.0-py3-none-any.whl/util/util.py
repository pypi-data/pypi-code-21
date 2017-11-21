import numpy as np

from keras.preprocessing.sequence import pad_sequences

def _padding_array(seqs, from_post, max_length, default):
    seqs_len = len(seqs)
    if seqs_len > max_length:
        if from_post:
            return seqs[0: max_length]
        else:
            start = seqs_len - max_length
            return seqs[start: ]
    elif seqs_len < max_length:
        append_times = max_length - seqs_len
        if from_post:
            list_to_be_append = seqs
        else:
            list_to_be_append = seqs[::-1]

        for _ in range(append_times):
            list_to_be_append.append(default)

        if from_post:
            return list_to_be_append
        else:
            return list_to_be_append[::-1]
    else:
        return seqs

def generate_padding_array(seqs, transfom_function,
                           default, max_length, inverse=False):
    n_seqs = len(seqs)
    temp_arr = _padding_array(
        transfom_function(seqs[0][::-1]), False, max_length, default
    )
    n_dim = temp_arr.shape[1]

    transformed_seqs = np.zeros(
        (n_seqs, max_length, n_dim),
        dtype=default.dtype,
    )
    if inverse:
        for idx, seq in enumerate(seqs):
            transformed_seqs[idx, :, :] = _padding_array(
                transfom_function(seq[::-1]), False, max_length, default
            )
    else:
        for idx, seq in enumerate(seqs):
            transformed_seqs[idx, :, :] = _padding_array(
                transfom_function(seq), False, max_length, default
            )
    return transformed_seqs
