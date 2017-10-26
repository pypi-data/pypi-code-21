import rx


class BaseFilter:
    def __init__(self, include_filters=None, exclude_filters=None):
        """
        Priority: exclude > include
        depth: int, depth of scanning.
            1 : only subdirs
            0 : only current dir
            -1: unlimited
        """
        super(__class__, self).__init__()
        self.include_filters = include_filters or []
        self.exclude_filters = exclude_filters or []

    def _apply(self, fs, path):
        raise NotImplementedError

    @classmethod
    def _filter_paths(cls, fs, path, files=None, dirs=None, exclude_files=None, exclude_dirs=None):
        infos = list(fs.filterdir(path,
                                  files=files,
                                  exclude_files=exclude_files,
                                  dirs=dirs,
                                  exclude_dirs=exclude_dirs))
        return (rx.Observable.from_(infos)
                  .map(lambda info: info.make_path(path)))

    @classmethod
    def _filter_files(cls, fs, path, include_filters, exclude_filters):
        return cls._filter_paths(fs, path, files=include_filters, exclude_files=exclude_filters, exclude_dirs=['*'])

    @classmethod
    def _filter_dirs(cls, fs, path, include_filters, exclude_filters=None):
        return cls._filter_paths(fs, path, exclude_files=['*'], dirs=include_filters, exclude_dirs=exclude_filters)

    def obv(self, fs, path='.'):
        return self._apply(fs, path)

    def lst(self, fs, path='.'):
        result = []
        self.obv(fs, path).subscribe(result.append)
        return result


class FilesFilter(BaseFilter):
    def __init__(self, include_filters=None, exclude_filters=None):
        super(__class__, self).__init__(include_filters, exclude_filters)

    def _apply(self, fs, path, depth=None):
        return self._filter_files(
            fs, path, self.include_filters, self.exclude_filters)


class DirectoriesFilter(BaseFilter):
    def __init__(self, include_filters=None, exclude_filters=None, depth=0):
        super(__class__, self).__init__(include_filters, exclude_filters)
        self.depth = depth

    @classmethod
    def _next_depth(cls, depth):
        return depth - 1 if depth > 0 else -1

    @classmethod
    def _need_recursive(cls, depth):
        return depth > 0 or depth == -1

    def _apply(self, fs, path, depth=None):
        if depth is None:
            depth = self.depth
        result = self._filter_dirs(
            fs, path, self.include_filters, self.exclude_filters)
        if self._need_recursive(depth):
            sub_results = (result.flat_map(
                lambda p: self._apply(fs, p, self._next_depth(depth))))
            result = rx.Observable.merge(result, sub_results)
        return result
