from .state import client_state


def install(process_name):
    client_state.process_name = process_name
