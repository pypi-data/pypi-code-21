import bob.paper.taslp_2017

extractor = bob.paper.taslp_2017.extractor.SpectralStatistics(
    win_length_ms = 32,
    win_shift_ms = 10,
    with_mean = True,
    with_std = True,
)
