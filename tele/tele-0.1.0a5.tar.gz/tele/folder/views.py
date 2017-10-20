import tele
import os
import json
import h5py


class Cell(tele.Cell):
    def __init__(self, meter_names, dir_path, filename_template):
        super().__init__(meter_names)
        self.dir_path = dir_path
        self.filename_template = filename_template

    def build_path(self, step_num):
        return os.path.join(self.dir_path, self.filename_template.format(step_num))

    def render(self, step_num, meters):
        raise NotImplementedError()


class View(tele.View):
    def __init__(self, meter_names, file_name):
        super().__init__(meter_names)
        self.file_name = file_name

    def build(self, dir_path):
        raise NotImplementedError()


class _JSONCell(Cell):
    def render(self, step_num, meters):
        path = self.build_path(step_num)
        values = {}
        for meter_name, meter in zip(self.meter_names, meters):
            values[meter_name] = meter.value()
        with open(path, 'w') as f:
            json.dump(values, f)


class JSON(View):
    def __init__(self, meter_names, file_name='metrics_{:04d}.json'):
        super().__init__(meter_names, file_name)

    def build(self, dir_path):
        return _JSONCell(self.meter_names, dir_path, self.file_name)


class _GrowingJSONCell(Cell):
    def render(self, step_num, meters):
        file_path = self.build_path(step_num)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                values = json.load(f)
        else:
            values = {}
        for meter_name, meter in zip(self.meter_names, meters):
            if meter_name not in values:
                values[meter_name] = []
            values[meter_name].append(meter.value())
        with open(file_path, 'w') as f:
            json.dump(values, f)


class GrowingJSON(View):
    def __init__(self, meter_names, file_name='metrics.json'):
        super().__init__(meter_names, file_name)

    def build(self, dir_path):
        return _GrowingJSONCell(self.meter_names, dir_path, self.file_name)


class _HDF5Cell(Cell):
    def __init__(self, meter_names, dir_path, filename_template, path_map):
        super().__init__(meter_names, dir_path, filename_template)
        self.path_map = path_map

    def render(self, step_num, meters):
        file_path = self.build_path(step_num)
        with h5py.File(file_path, 'w') as f:
            for meter_name, meter in zip(self.meter_names, meters):
                if meter_name in self.path_map:
                    h5_path = self.path_map[meter_name]
                else:
                    h5_path = meter_name
                f.create_dataset(h5_path, data=meter.value())


class HDF5(View):
    def __init__(self, meter_names, file_name='data_{:04d}.h5', path_map=None):
        super().__init__(meter_names, file_name)
        if path_map is None:
            path_map = {}
        self.path_map = path_map

    def build(self, dir_path):
        return _HDF5Cell(self.meter_names, dir_path, self.file_name, self.path_map)
