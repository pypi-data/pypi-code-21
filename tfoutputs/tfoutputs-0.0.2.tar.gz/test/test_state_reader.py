import pytest
import json
from tfoutputs.state_reader import StateReader

class TestStateReader (object):


    @pytest.fixture()
    def state_reader(self):
        return StateReader(['./test/fixtures/terraform.tfstate', './test/fixtures/terraform2.tfstate'])

    def test_load_outputs(self, state_reader):
        state_reader.load_outputs()
        assert state_reader.allowed_ips == '10.5.1.6/32'

    def test_parse_outputs(self, state_reader):
        module = json.loads("""
        {
            "path": [
                "root"
            ],
            "outputs": {
                "allowed_ips": {
                    "sensitive": false,
                    "type": "string",
                    "value": "10.5.1.6/32"
                },
                "services_z1_count": {
                    "sensitive": false,
                    "type": "string",
                    "value": "1"
                },
                "services_z2_count": {
                    "sensitive": false,
                    "type": "string",
                    "value": "0"
                }
            }
        }
        """)
        state_reader.parse_outputs(module)
        assert 'services_z2_count' in state_reader.outputs


