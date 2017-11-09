# Copyright 2016 Internap.
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


def a_response_data(**overrides):
    return apply_kwargs(overrides, {
        "status": True,
        "error_code": None,
        "error_message": "",
        "data": {},
    })


def apply_kwargs(kwargs, default_kwargs):
    for k, v in kwargs.items():
        if isinstance(v, dict):
            default_kwargs[k] = apply_kwargs(v, default_kwargs[k])
        else:
            default_kwargs[k] = v
    return default_kwargs
