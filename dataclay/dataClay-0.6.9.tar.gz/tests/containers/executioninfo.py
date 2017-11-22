import unittest
import uuid

from .generic import ContainerGeneric


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class ExecutionInfoTest(ContainerGeneric):
    params = [
        ("name", u"Implementation_Name"),
        ("arg_type_signatures", [u"I", u"F", u"I", u"Lsome/random/class;"]),
        ("arg_names", [u"param_one", u"param_two", u"param_three", u"last_param"]),
        ("return_type_signature", u"V"),
        ("modify_state", True),
        ("implementation_id", uuid.uuid4()),
    ]

    mutable_params = [
        ("name", u"Implementation_Name_Mutable"),
        ("return_type_signature", u"Z"),
        ("modify_state", False),
        ("implementation_id", uuid.uuid4()),
    ]

    nullable_field = []

    class_under_test = ExecutionInfo


if __name__ == '__main__':
    unittest.main()
