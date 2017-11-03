from __future__ import absolute_import, division, print_function
from future.utils import with_metaclass
import autest.glb as glb


class _test_enity__metaclass__(type):
    def __call__(cls, *lst, **kw):
        # make instance of the class
        inst = type.__call__(cls, *lst, **kw)
        # given which class this is we look up
        # in a dictionary which items we want to add
        cls_info = glb.runable_items.get(cls, {})
        # add any items we want to add to the runtest item.
        for k, v in cls_info.items():
            setattr(inst, k, v(inst._Runable))
        return inst
