from ctypes import c_float
global cats, svm_cache, svm_media, media_index, cache_hits, svms_trained, c_index_array, svm_buffer, debug_dic_path
feat_size = 2048
feature_t = c_float * feat_size
