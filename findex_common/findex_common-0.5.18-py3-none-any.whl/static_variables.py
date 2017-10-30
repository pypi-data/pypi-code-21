import sys
import os

user_agent = "FindexCrawl - https://github.com/skftn/findex-gui"


class Types(object):
    def __init__(self):
        self.data = {}

    def id_by_name(self, name):
        if name in self.data:
            return self.data[name]

    def name_by_id(self, id):
        if sys.hexversion >= 0x03000000:
            gen = self.data.items()
        else:
            gen = self.data.iteritems()

        for k, v in gen:
            if v == id:
                return k

    def get_names(self):
        return self.data.keys()


class FileCategories(Types):
    def __init__(self):
        super(FileCategories, self).__init__()
        
        self.data = {
            "unknown": 0,
            "documents": 1,
            "movies": 2,
            "music": 3,
            "images": 4
        }


class FileProtocols(Types):
    def __init__(self):
        super(FileProtocols, self).__init__()

        self.data = {
            "ftp": 0,
            "fs": 1,
            "smb": 2,
            "sftp": 3,
            "http": 4,
            "https": 5,
            "ftps": 6
        }


class SearchParameters(Types):
    def __init__(self):
        super(SearchParameters, self).__init__()

        self.data = {
            "cats": "file_categories",
            "exts": "file_extensions",
            "type": "file_type",
            "proto": "protocols"
        }


class PopcornParameters(Types):
    def __init__(self):
        super(PopcornParameters, self).__init__()

        self.data = {
            "genres": "genres",
            "actors": "actors",
            "year": "year",
            "min_rating": "min_rating",
            "director": "director"
        }


class DefaultPorts(Types):
    def __init__(self):
        super(DefaultPorts, self).__init__()

        self.data = {
            "http": 80,
            "ssh": 22,
            "https": 443,
            "ftp": 21
        }


class ResourceStatus(Types):
    def __init__(self):
        super(ResourceStatus, self).__init__()

        self.data = {
            "idle": 0,
            "actively crawling": 1,
            "actively calculating folder sizes": 2,
            "actively gathering metadata": 3,
            "task scheduled": 4,
            "locked": 5
        }
