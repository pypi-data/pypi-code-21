from decorator import getargspec, decorate
from inspect import getcallargs

__author__ = 'abarcelo'


# This should be either a COMPSs class, or a storage.api one
# or simply a dictionary
class Hints(dict):
    pass


def merge_reduce(partial_result, reduce_func):
    """Almost verbatim copy-paste, tree-reduce from slides"""
    # from pycompss.api.api import compss_wait_on
    n = len(partial_result)
    act = [j for j in range(n)]
    while n > 1:
        aux = []
        for i in range(0, n, 2):
            reduce_func(partial_result[act[i]],
                        partial_result[act[i+1]])
            aux.append(act[i])
        act = aux
        n = len(act)
    return partial_result[0]


class LocalIteration(object):
    """Used to decorate functions to become aware of fancy iteration"""

    def __init__(self, iterate_by, reduce_with=None, reduce_schema=merge_reduce, no_wait=False):
        self._iterate_by = iterate_by
        self._reduce_with = reduce_with
        self._reduce_schema = reduce_schema
        self._no_wait = no_wait

    def __call__(self, f):
        self._argspec = getargspec(f)

        def injected_func(func, *args, **kwargs):
            # Preparation (performed before the call)
            # Obtain the parameter to be local-iterated
            callargs = getcallargs(func, *args, **kwargs)
            if self._iterate_by in callargs:
                collection = callargs.pop(self._iterate_by)
            elif self._iterate_by in callargs[self._argspec.keywords]:
                collection = callargs[self._argspec.keywords].pop(self._iterate_by)
            else:
                raise TypeError("Could not find argument `%s` amongst parameters",
                                self._iterate_by)

            new_args = [callargs[i]
                        for i in self._argspec.args
                        ] + list(callargs[self._argspec.varargs])
            new_kwargs = callargs[self._argspec.keywords]

            iterators = collection.get_local_iterators()

            partial_result = list()
            for dataservice, local_it in iterators:
                new_kwargs[self._iterate_by_name] = local_it

                ####################################################
                # COMPSs HINTS
                ##############
                new_kwargs["__compss_hints"] = Hints(
                    dataservice=dataservice
                )

                partial_result.append(func(*new_args, **new_kwargs))

            # Resolution (performed after the call)
            if self._reduce_with:
                reduced_result = self._reduce_schema(partial_result, self._reduce_with)
                if self._no_wait:
                    return reduced_result
                else:
                    return compss_wait_on(reduced_result)
            else:
                return None
                #no posar aixo


        return decorate(f, injected_func)
