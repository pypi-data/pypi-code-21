from tfoutputs.state_reader import StateReader
from tfoutputs.stateconfigurator import StateConfigurator


def load(config):
    sc = StateConfigurator(config)
    sc.files_from_backend()
    sr = StateReader(sc.state_files)
    sr.load_outputs()
    sc.cleanup()
    return sr
