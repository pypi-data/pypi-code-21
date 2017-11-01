from typing import List, Tuple, Dict
import re


def split_oneline(str: str) -> Dict[str, float]:
    ret_list = list()

    for tag in str.split(sep=' '):
        ret_list.append(_parse_tag(tag))

    return dict(ret_list)


def _parse_tag(tag: str) -> Tuple[str, float]:
    tag_name, tag_time = tag.split(sep=":")
    return tag_name, float(_filter_float(tag_time))


def _filter_float(my_string: str) -> str:
    return re.sub('[^0-9.]', "", my_string)
