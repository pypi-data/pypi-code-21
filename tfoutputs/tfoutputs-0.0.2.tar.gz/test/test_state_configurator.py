from tfoutputs.stateconfigurator import StateConfigurator
import inspect
import pytest
import os
import tempfile


class TestStateConfigurator(object):
    @pytest.fixture
    def stateconfigurator(self):
        config = {'backend': 's3',
                  'options': {'bucket_name': 'fake.bucket.for.vcr',
                              'bucket_key': 'terraform.tfstate',
                              'bucket_region': 'eu-west-1'
                              }
                  }
        return StateConfigurator(config)

    def test_stateconfigurator_init(self, stateconfigurator):
        assert stateconfigurator.config[0].get('backend') == 's3'
        assert stateconfigurator.config[0]['options']['bucket_name'] == 'fake.bucket.for.vcr'
        assert stateconfigurator.config[0]['options']['bucket_key'] == 'terraform.tfstate'

    def test_stateconfigurator_setter_errors(self):
        config = 'lol'
        with pytest.raises(TypeError):
            StateConfigurator(config)

    def test_backend_for(self):
        backend = StateConfigurator.backend_for('s3')
        assert inspect.isclass(backend)

    def test_files_from_backend(self, stateconfigurator, vcr_test):
        with vcr_test.use_cassette('test_file_from_backend.yml'):
            stateconfigurator.files_from_backend()
            assert len(stateconfigurator.state_files) == 1
    def test_cleanup(self, stateconfigurator):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Word!")
            f.flush()
            f.seek(0)
            assert b"Word!" == f.read()
            stateconfigurator.state_files = f.name
        stateconfigurator.cleanup()
        with pytest.raises(FileNotFoundError):
            os.stat(stateconfigurator.state_files[0])
