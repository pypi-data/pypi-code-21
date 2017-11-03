import os
import sys

parallelism_serial = "serial"
parallelism_mpi = "mpi"
parallelism_embarassing = "embarassing"

class Stage:
    def __init__(self):
        self.config_dir = os.environ['DESC_CONFIG']
        self.input_dir = os.environ['DESC_INPUT']
        self.output_dir = os.environ['DESC_OUTPUT']
        self.parallelism = None

    @classmethod
    def main(cls):
        stage = cls()
        stage.run()

    def get_input_filenames(cls):
        return [self.get_input_filename(name) for name in self.inputs.keys()]

    def get_output_filenames(cls):
        return [self.get_output_filename(name) for name in self.outputs.keys()]


    def get_input_filename(cls, name):
        filetype = self.inputs[name]
        filename = "{}.{}".format(name,filetype)
        return filename

    def get_output_filename(cls, name):
        filetype = self.outputs[name]
        filename = "{}.{}".format(name,filetype)
        return filename

    def get_config_path(self, name):
        "Return the complete path to a configuration file from the tag name"
        filename = self.config[name]
        return os.path.join(self.config_dir, filename)

    def get_input_path(self, name):
        "Return the complete path to an input file from the tag name"
        filename = self.get_input_filename(name)
        return os.path.join(self.input_dir, filename)

    def get_output_path(self, name):
        "Return the complete path to an output file from the tag name"
        filename = self.get_output_filename(name)
        return os.path.join(self.output_dir, filename)

    def _setup_parallel_runtime(self):
        parallelism = os.environ.get("DESC_PARALLEL", parallelism_serial)
        self.parallelism = parallelism
        self._comm = None
        if parallelism == parallelism_serial:
            self._rank = 0
            self._size = 1
        elif parallelism == parallelism_embarassing:
            self._rank = os.environ['DESC_RANK']
            self._size = os.environ['DESC_SIZE']
        elif parallelism == parallelism_mpi:
            from mpi4py.MPI import COMM_WORLD
            self._comm = comm
            self._rank = comm.Get_rank()
            self._size = comm.Get_size()
        else:
            self.parallelism = None
            raise ValueError("Unknown parallelism mode: {}".format(parallelism))

    def get_comm(self):
        if self.parallelism is None:
            self._setup_parallel_runtime()
        return self._comm

    def get_rank(self):
        if self.parallelism is None:
            self._setup_parallel_runtime()
        return self._rank

    def get_size(self):
        if self.parallelism is None:
            self._setup_parallelism()
        return self._size
