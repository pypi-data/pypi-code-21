from dmu_utils.misc import get_call_repr


def test_get_call_repr_for_func_no_args():
    def no_args_func():
        pass

    call_repr = get_call_repr(no_args_func)
    assert call_repr == 'no_args_func()'


def test_get_call_repr_for_func_args_and_kwargs():
    def args_and_kwargs_func(arg1, arg2, kwarg1, kwarg2, kwarg3):
        pass

    from decimal import Decimal
    call_repr = get_call_repr(args_and_kwargs_func, (5, 'string'),
                              {'kwarg1': 5, 'kwarg2': 'string', 'kwarg3': Decimal(6)})
    assert call_repr == ("args_and_kwargs_func(5, 'string', "
                         "kwarg1=5, kwarg2='string', kwarg3=Decimal('6'))")
