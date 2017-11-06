# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ------------------------------------------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f %z"
TIME_FORMAT = "%H:%M:%S.%f %z"

ERR_PYTHON_DATA_NOT_JSON_SERIALIZABLE = "Invalid python data sample provided: ensure that the data is fully JSON " \
                                        "serializable to be able to generate swagger schema from it. Actual error: {}"
ERR_FILE_NOT_SUPPORTED_FOR_NUMPY = "Invalid input file type provided: {}. Only .json, .csv, .tsv, and .arff files " \
                                   "currently supported for conversion to Numpy Array."
ERR_FILE_NOT_SUPPORTED_FOR_PANDAS = "Invalid input file type provided: {}. Only .json, .csv, .tsv, and .arff files " \
                                    "currently supported for conversion to Pandas Dataframe."
ERR_FILE_NOT_SUPPORTED_FOR_PYTHON = "Invalid input file type provided: {}. Only .json, .csv, .tsv, and .arff files " \
                                    "currently supported for conversion to Python List."
ERR_FILE_NOT_SUPPORTED_FOR_SPARK = "Invalid input file type provided: {}. Only .json, .csv, .tsv, and .parquet files " \
                                   "currently supported for conversion to Spark Dataframe"
