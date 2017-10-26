class FS:
    def __init__(self, fs_or_path):
        from .config import config
        if isinstance(fs_or_path, str):
            self.fs = config.default_fs(Path(fs_or_path).abs)
            self.need_close = True
        else:
            self.fs = fs_or_path
            self.need_close = False

    def __enter__(self):
        return self.fs

    def __exit__(self, type, value, trackback):
        if self.need_close:
            self.fs.close()
