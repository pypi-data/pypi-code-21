import tele.folder.views
import os


class Conf(tele.Conf):
    def __init__(self, dir_path):
        super().__init__()
        self.dir_path = dir_path

    def make_auto_view(self, meter_name, meter):
        return None

    def build(self, view_list):
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        cell_list = [view.build(self.dir_path) for view in view_list]
        return tele.Sink(cell_list)
