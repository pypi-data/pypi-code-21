from overlock import __version__


class _State:
    version = __version__
    process_name = "unknown"


client_state = _State()
