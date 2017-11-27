from hypothesis import given
from hypothesis.strategies import integers

from pysiren.helpers.pagination import Pagination


def test_basic_usage():
    pagination = Pagination(1, 25, 101)

    assert(pagination.page == 1)
    assert(pagination.page_size == 25)
    assert(pagination.total == 101)
    assert(pagination.pages_count == 5)

    assert(not pagination.has_prev)
    assert pagination.has_next


def test_incorrect_init():
    assert(Pagination(1, 0, 100).page_size == 1)
    assert (Pagination(1, -1, 100).page_size == 1)

    assert (Pagination(1, 25, 0).total == 0)
    assert (Pagination(1, 25, -1).total == 0)

    assert (Pagination(1, 0, 0).total == 0)
    assert (Pagination(1, 0, 0).pages_count == 0)

    assert (Pagination(1, -1, -1).total == 0)
    assert (Pagination(1, -1, -1).pages_count == 0)


def test_has_prev_next_edges():
    pagination = Pagination(1, 25, 101)
    assert (not pagination.has_prev)
    assert pagination.has_next

    pagination = Pagination(5, 25, 101)
    assert pagination.has_prev
    assert (not pagination.has_next)


@given(integers(min_value=2, max_value=50))
def test_has_prev_next(i):
    pagination = Pagination(i, 5, 5*50 + 1)
    assert(pagination.has_prev)
    assert(pagination.has_next)


@given(integers())
def test_total_pages_count_edge(i):
    assert (Pagination(1, i, 0).pages_count == 0)
    assert (Pagination(1, i, 1).pages_count == 1)


@given(integers(min_value=2))
def test_total_pages_count(i):
    assert (Pagination(1, i, i).pages_count == 1)
    assert (Pagination(1, i, i + 1).pages_count == 2)

    assert (Pagination(1, i, i * 2 - 1).pages_count == 2)
    assert(Pagination(1, i, i * 2).pages_count == 2)
    assert (Pagination(1, i, i * 2 + 1).pages_count == 3)


@given(integers(min_value=1, max_value=50))
def test_offset(i):
    assert(Pagination(1, i, 10).offset() == 0)
    assert(Pagination(i, 20, 1000).offset() == 20 * (i - 1))


def test_offset_incorrect_page():
    assert(Pagination(-1, 10, 100).offset() == 0)
    assert (Pagination(51, 20, 1000).offset() == 1000 - 20)
    assert(Pagination(100000, 20, 1000).offset() == 1000 - 20)


@given(integers(min_value=1, max_value=3))
def test_pagination_set_small_total(i):
    assert(Pagination(i, 10, 0).get_pagination_set() == {})
    assert(Pagination(i, 10, 1).get_pagination_set() == {'first': 1, 'self': 1, 'last': 1})
    assert (Pagination(i, 10, 9).get_pagination_set() == {'first': 1, 'self': 1, 'last': 1})
    assert (Pagination(i, 10, 10).get_pagination_set() == {'first': 1, 'self': 1, 'last': 1})


@given(integers(min_value=4, max_value=50))
def test_pagination_set(i):
    assert(Pagination(i, 10, 0).get_pagination_set() == {})
    assert (Pagination(i, 10, 1).get_pagination_set() == {'first': 1, 'self': 1, 'last': 1})

    expected = {
        'first': 1,
        'prev': i - 1,
        'self': i,
        'next': i + 1,
        'last': 53
    }
    assert(Pagination(i, 10, 10*53).get_pagination_set() == expected)


@given(integers(min_value=51, max_value=53))
def test_pagination_set_last_pages_count(i):
    expected = {
            'first': 1,
            'prev': i - 1,
            'self': i,
            'last': 53
    }
    if i < 53:
        expected['next'] = i + 1
        
    result = Pagination(i, 10, 53*10).get_pagination_set()
    assert(result == expected)
