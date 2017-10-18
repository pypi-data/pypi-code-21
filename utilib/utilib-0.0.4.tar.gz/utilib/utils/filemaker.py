from io import BytesIO
import pyexcel


def make_excel(record_list,
               file_type='xlsx', sheet_name='sheet1', headers=[]):
    record_list.insert(0, headers)
    _out = BytesIO()
    pyexcel.Sheet(record_list).save_to_memory(file_type, _out)
    return _out
