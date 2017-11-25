class DictFileOpener:
    """ Context manager to safely open multiple files and ensure they are closed on exit or error. """
    def __init__(self, files):
        """ Open all the files and store the file handles in a dict, referenced by file name. """
        self.file_data = {filename: open(filename, 'r') for filename in files}

    def __enter__(self):
        return self.file_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Close all the file handles. """
        for file_handle in self.file_data.values():
            file_handle.close()
