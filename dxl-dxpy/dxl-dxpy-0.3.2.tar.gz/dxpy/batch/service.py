import rx


class Mapper:
    @classmethod
    def ls(cls, fs, filter_, infos=None):
        # TODO convert to true observalbes
        infos = infos or []
        paths = filter_.get_list(self.fs)
        result_dct = {'path': paths}
        for k in infos:
            if 'size' == k:
                sizes = [fs.getdetails(p).size for p in paths]
                result_dct.update({'size': sizes})
        results = zip(*(result_dct[k] for k in result_dct))
        # return rx.Observable.from_(results)
        return results

    @classmethod
    def map(cls, fs, filter_, callback):
        paths = filter_.get_list(fs)
        for p in paths:
            callback(p)

    @classmethod
    def broadcast(cls, fs, filter_, content):
        """
        Copy content to all filtered elements.
        """
        pass


class Reducer:
    @classmethod
    def cat(cls, files):
        """
        Inputs:
            files: a list/observable of File.
        """
        pass
