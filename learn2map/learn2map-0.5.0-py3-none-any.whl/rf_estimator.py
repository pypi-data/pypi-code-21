#!/usr/bin/env python

import os
import sys
import getopt
import learn2map.raster_tools as rt
import learn2map.data_learning as dl


def estimator(in_file_list, out_file_name, n_estimators_step=500, min_samples_step=18, max_feature_step=200):
    """

    :param in_file_list:
    :param out_file_name:
    :param max_feature_step:
    :param n_estimators_step:
    :param min_samples_step:
    :return:
    """

    # find columns of mask and y from input txt file
    with open(in_file_list, 'r') as f:
        file_names = f.readlines()
        mask_column = '{}_b1'.format(os.path.basename(os.path.splitext(file_names[0])[0]))
        y_column = '{}_b1'.format(os.path.basename(os.path.splitext(file_names[1])[0]))

    # make vrt file for all input files
    out_vrt = '{}.vrt'.format(out_file_name)
    field_names = rt.build_stack_vrt(in_file_list, out_vrt)

    # save valid training pixels to hdf5
    out_training_h5 = '{}_training.h5'.format(out_file_name)
    rt.raster_to_h5(out_vrt, out_training_h5, field_names, y_column, mask_valid_range=0, lines=100)

    # save valid environmental pixels to hdf5
    out_env_h5 = '{}_env.h5'.format(out_file_name)
    rt.raster_to_h5(out_vrt, out_env_h5, field_names, mask_column, mask_valid_range=0, lines=100)

    # set up gridlearn object
    learning0 = dl.GridLearn(out_training_h5, y_column=y_column, mask_column=[mask_column, 'x', 'y'])

    # RF learning
    learning0.setup_rf_model()
    params = {
        'learn__n_estimators': list(range(50, 501, n_estimators_step)),
        'learn__min_samples_split': list(range(2, 100, min_samples_step)),
        'learn__max_features': list(range(1, int((len(field_names)) - 1), max_feature_step)),
    }
    learning0.tune_param_set(params, k=3)
    # learning0.sklearn_test(out_training_h5, plot_limit=(0, 50))

    # RF prediction
    out_file_h5 = '{}_est.h5'.format(os.path.splitext(out_env_h5)[0])
    learning0.predict_bigdata(out_env_h5, out_file_h5)
    out_csv = '{}.csv'.format(os.path.splitext(out_file_h5)[0])
    rt.h5_to_csv(out_file_h5, out_csv)

    # convert hdf5 to grid
    # print(os.getcwd())
    out_raster = '{}_raster_mean'.format(os.path.splitext(out_csv)[0])
    rt.ogrvrt_to_grid(file_names[0].strip(), out_csv, 'x', 'y', 'Est', out_raster, a_interp='nearest')
    out_raster = '{}_raster_err'.format(os.path.splitext(out_csv)[0])
    rt.ogrvrt_to_grid(file_names[0].strip(), out_csv, 'x', 'y', 'Err', out_raster, a_interp='nearest')


# if __name__ == '__main__':
def main():
    in_file_list = '../data/test_data/output/mchtest_inputs.txt'
    out_file_name = '../data/test_data/output/mchtest'
    n_estimators_step = 500
    min_samples_step = 100
    max_feature_step = 200
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:s:f:")
    except getopt.GetoptError:
        print(
            'rf_estimator -i "inputfilelist" -o "outputfile w/o extension" '
            '[-n "n_estimators_step" -s "min_samples_step" -f "max_feature_step"]'
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'rf_estimator -i "inputfilelist" -o "outputfile w/o extension" '
                '[-n "n_estimators_step" -s "min_samples_step" -f "max_feature_step"]'
            )
            sys.exit()
        elif opt in ("-i"):
            in_file_list = arg
        elif opt in ("-o"):
            out_file_name = arg
        elif opt in ("-n"):
            n_estimators_step = int(arg)
        elif opt in ("-s"):
            min_samples_step = int(arg)
        elif opt in ("-f"):
            max_feature_step = int(arg)

    estimator(
        in_file_list, out_file_name, n_estimators_step=n_estimators_step,
        min_samples_step=min_samples_step, max_feature_step=max_feature_step
    )


def csv_output():
    in_file_list = '../data/test_data/output/mchtest_inputs.txt'
    out_file_name = '../data/test_data/output/mchtest'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    except getopt.GetoptError:
        print(
            'csv_output -i "input" -o "outname"'
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'csv_output -i "input" -o "outname"'
            )
            sys.exit()
        elif opt in ("-i"):
            in_file_list = arg
        elif opt in ("-o"):
            out_file_name = arg

    with open(in_file_list, 'r') as f:
        file_names = f.readlines()
        y_column = '{}_b1'.format(os.path.basename(os.path.splitext(file_names[0])[0]))

    # make vrt file for all input files
    out_vrt = '{}.vrt'.format(out_file_name)
    field_names = rt.build_stack_vrt(in_file_list, out_vrt)

    # save valid pixels to hdf5
    out_file_h5 = '{}.h5'.format(out_file_name)
    rt.raster_to_h5(out_vrt, out_file_h5, field_names, y_column, mask_valid_range=0, lines=100)

    # convert hdf5 to csv
    out_csv = '{}.csv'.format(out_file_name)
    rt.h5_to_csv(out_file_h5, out_csv)
