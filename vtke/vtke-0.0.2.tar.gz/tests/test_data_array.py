from vtke.data_array import DataArray


def test_serialize_data_ascii():
    da = DataArray()
    da.type = 'Int32'
    da.format = 'ascii'
    da.data = (12, 213, 34)

    assert da._serialize_data() == '12 213 34'


def test_serialize_data_binary_ints():
    da = DataArray()
    da.type = 'Int64'
    da.format = 'binary'
    da.data = (4, 8, 12, 16, 20, 24)

    assert da._serialize_data() == 'MAAAAAQAAAAAAAAACAAAAAAAAAAMAAAAAAAAABAAAAAAAAAAFAAAAAAAAAAYAAAAAAAAAA=='

    assert da._serialize_data(compress=True) == 'AQAAAACAAAAwAAAAGAAAAA==eJxjYYAADijNA6UFoLQIlJaA0gAHMABV'


def test_serialize_data_binary_floats():
    da = DataArray()
    da.type = 'Float32'
    da.format = 'binary'
    da.data = (-1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0,
               0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0,
               0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1)

    assert da._serialize_data() == 'IAEAAAAAgL8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAgL8AAAAAAAAAAAA' \
                                   'AgD8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAAAAAAI' \
                                   'C/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAIA/AAAAA' \
                                   'AAAAAAAAIA/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAvwAAAAAA' \
                                   'AAAAAACAvwAAAAAAAAAAAACAvwAAAAAAAAAAAACAvwAAAAAAAAAAAACAPwAAAAAAAAAAAAC' \
                                   'APwAAAAAAAAAAAACAPwAAAAAAAAAAAACAPw=='

    assert da._serialize_data(compress=True) == 'AQAAAACAAAAgAQAAGQAAAA==eJxjYGjYzwAHRLHtSWMTbe6gtAMA+HsX6Q=='
