from wesci.timer import Timer
from wesci.hash import Hash
from os.path import splitext
from csv import reader


class Files(object):

    PREVIEW_TEXT_LINES = 10
    PREVIEW_TEXT_LINE_WIDTH = 80
    PREVIEW_CSV_ROWS = 10
    PREVIEW_CSV_COLUMNS = 10

    @staticmethod
    def generate_data_for_log(files_dict):
        data_for_log = {}
        for name, path in files_dict.items():
            data, read_duration = Files.__get_file_data_and_duration_of_read(
                path)
            file_hash, hash_duration = Files.__calc_hash_and_duration(data)
            size = len(data)
            preview, preview_duration = Files.__get_preview(path)
            data_for_log[name] = Files.__format_data_for_log(
                path,
                file_hash,
                size,
                preview,
                read_duration,
                hash_duration,
                preview_duration)
        return data_for_log

    @staticmethod
    def __calc_hash_and_duration(file_data):
        with Timer() as timer:
            res = Hash.hash(file_data)
        return res, timer.duration_ms()

    @staticmethod
    def __get_file_data_and_duration_of_read(file_path):
        with Timer() as timer:
            with open(file_path, 'rb') as f:
                file_data = f.read()
        return file_data, timer.duration_ms()

    @staticmethod
    def __get_txt_preview(path):
        preview = []
        with open(path, 'r') as f:
            for line in f:
                preview.append(line[:Files.PREVIEW_TEXT_LINE_WIDTH])
                if len(preview) == Files.PREVIEW_TEXT_LINES:
                    break
        return '\n'.join(preview)

    @staticmethod
    def __get_csv_preview(path):
        preview = []
        with open(path, 'r') as f:
            rows = reader(f)
            for row in rows:
                preview.append(','.join(row[:Files.PREVIEW_CSV_COLUMNS]))
                if len(preview) == Files.PREVIEW_CSV_ROWS:
                    break
        return '\n'.join(preview)

    @staticmethod
    def __get_preview(path):
        with Timer() as timer:
            preview = ''
            t, ext = splitext(path)
            ext = ext.lower()
            if ext == '.txt':
                preview = Files.__get_txt_preview(path)
            if ext == '.json':
                preview = Files.__get_txt_preview(path)
            elif ext == '.csv':
                preview = Files.__get_csv_preview(path)
        return preview, timer.duration_ms()

    @staticmethod
    def __format_data_for_log(
            path,
            file_hash,
            size,
            preview,
            read_duration,
            hash_duration,
            preview_duration):
        return {'path': path,
                'hash': file_hash,
                'size': size,
                'preview': preview,
                'timing': {
                    'file_read_ms': read_duration,
                    'hash_calc_ms': hash_duration,
                    'preview_ms': preview_duration},
                }
