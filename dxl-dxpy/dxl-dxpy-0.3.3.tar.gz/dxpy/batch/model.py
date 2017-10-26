import rx


class BaseFilter:
    def __init__(self, include_filters=None, exclude_filters=None, depth=1):
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
        self.depth = depth

    def _apply(self, fs, path, depth):
        raise NotImplementedError

    def get_observable(self, fs):
        return self._apply(fs, '.', self.depth)

    def get_list(self, fs):
        result = []
        self.get_observable(fs).subscribe(result.append)
        return result


class FilesFilter(BaseFilter):
    def __init__(self, include_filters=None, exclude_filters=None, depth=1):
        super(__class__, self).__init__(include_filters,
                                        exclude_filters, depth)

    def _apply(self, fs, path='.', depth=None):
        if depth is None:
            depth = self.depth
        infos = fs.filterdir(path,
                             files=self.include_filters,
                             exclude_files=self.exclude_filters,
                             exclude_dirs=['*'])
        result = (rx.Observable.from_(infos)
                  .map(lambda info: info.make_path(path)))
        if not depth == 0:
            infos = fs.filterdir(path,
                                 exclude_files=['*'],
                                 exclude_dirs=self.exclude_filters)
            sub_results = (rx.Observable.from_(infos)
                           .map(lambda info: info.make_path(path))
                           .flat_map(lambda p: self._apply(fs, p, depth - 1 if depth > 0 else -1)))
            result = rx.Observable.merge(result, sub_results)
        return result


class DirsFilter(BaseFilter):
    def __init__(self, include_filters=None, exclude_filters=None, depth=1):
        super(__class__, self).__init__(include_filters,
                                        exclude_filters,  depth)

    def _apply(self, fs, path='.', depth=None):
        if depth is None:
            depth = self.depth
        infos = fs.filterdir(path,
                             exclude_files=['*'],
                             dirs=self.include_filters,
                             exclude_dirs=self.exclude_filters)
        result = (rx.Observable.from_(infos)
                  .map(lambda info: info.make_path(path)))
        if not depth == 0:
            infos = fs.filterdir(path,
                                 exclude_files=['*'],
                                 exclude_dirs=self.exclude_filters)
            sub_results = (rx.Observable.from_(infos)
                           .map(lambda info: info.make_path(path))
                           .flat_map(lambda p: self._apply(fs, p, depth - 1 if depth > 0 else -1)))
            result = rx.Observable.merge(result, sub_results)
        return result


class CombinedFileter(BaseFilter):
    def __init__(self, filters):
        super(__class__, self).__init__()
        self.filters = filters

    def _apply(self, fs):
        # TODO: add merge observable operation
        pass
