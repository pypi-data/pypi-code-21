# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def form_encode(data):
    exploded_data = {}
    for k, v in data.items():
        items = _explode_enumerable(k, v)
        for new_key, new_val in items:
            exploded_data[new_key] = new_val
    return exploded_data


def form_encode_without_files(data):
    return form_encode({k: v for k, v in data.items() if k is not 'files'})


def _explode_enumerable(k, v):
    exploded_items = []
    if isinstance(v, list) or isinstance(v, tuple):
        if len(v) == 0:
            exploded_items.append((k, v))
        else:
            for idx, item in enumerate(v):
                current_key = '{}[{}]'.format(k, idx)
                exploded_items.extend(_explode_enumerable(current_key, item))
    elif isinstance(v, dict):
        if len(v) == 0:
            exploded_items.append((k, v))
        else:
            for idx, item in v.items():
                current_key = '{}[{}]'.format(k, idx)
                exploded_items.extend(_explode_enumerable(current_key, item))
    else:
        exploded_items.append((k, v))
    return exploded_items
