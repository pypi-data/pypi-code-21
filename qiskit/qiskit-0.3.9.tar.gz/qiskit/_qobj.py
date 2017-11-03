# -*- coding: utf-8 -*-
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
# =============================================================================
"""Models for QObj and its related components."""


class Qobj(object):
    def __init__(self, id_, config=None, circuits=None):
        self.id_ = id_
        self.config = config or 12
        self.circuits = circuits or []


class QobjConfig(object):
    def __init__(self, max_credits, shots, backend):
        """
        """
        self.max_credits = max_credits
        self.shots = shots
        self.backend = backend

        if max_credits:
            self.ss = 28


class QobjCircuit(object):
    def __init__(self, name, compiled_circuit, ):

q = QobjConfig(backend=2, max_credits=None, shots=3)

print(q.ss)

"""
qobj =
    {
        id: --job id (string),
        config: -- dictionary of config settings (dict)--,
            {
            "max_credits" (online only): -- credits (int) --,
            "shots": -- number of shots (int) --.
            "backend": -- backend name (str) --
            }
        circuits:
            [
                {
                "name": --circuit name (string)--,
                "compiled_circuit": --compiled quantum circuit (JSON format)--,
                "compiled_circuit_qasm": --compiled quantum circuit (QASM format)--,
                "config": --dictionary of additional config settings (dict)--,
                    {
                    "coupling_map": --adjacency list (dict)--,
                    "basis_gates": --comma separated gate names (string)--,
                    "layout": --layout computed by mapper (dict)--,
                    "seed": (simulator only)--initial seed for the simulator (int)--,
                    }
                },
                ...
            ]
        }
"""