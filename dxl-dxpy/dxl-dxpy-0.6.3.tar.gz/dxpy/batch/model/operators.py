import rx
from fs import copy, path

class Mapper:
    @classmethod
    def ls(cls, fs, paths, infos=None):
        # TODO convert to true observalbes
        infos = infos or ['syspath']
        result_dct = dict()
        for k in infos:
            if k == 'syspath':
                result_dct.update({k: [fs.syspath(p) for p in paths]})
            elif k == 'size':
                result_dct.update({k: [fs.getdetails(p).size for p in paths]})
        results = zip(*(result_dct[k] for k in result_dct))
        # return rx.Observable.from_(results)
        return results

    @classmethod
    def map(cls, fs, paths, callback):
        return [callback(fs, p) for p in paths]

    @classmethod
    def broadcast(cls, fs, paths, path_content):
        """
        Copy content to all paths.
        """
        return [copy.copy_file(fs, path_content, fs, p) for p in paths]

    @classmethod
    def broadcast_directory(cls, fs, paths, path_content):
        name = path.basename(path_content)
        return [copy.copy_file(fs, path_content, fs, path.join(p, name)) for p in paths]


class Reducer:
    @classmethod
    def cat(cls, fs, paths):
        """
        Inputs:
            files: a list/observable of File.
        """
        pass