import unittest

import mock

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.devices.runners.configuration_runner import _validate_custom_params


class TestValidateCustomParams(unittest.TestCase):
    def test_validate_custom_params(self):
        """Check that method will raise Exception if there is no "custom_params" attribute in the object"""
        custom_params = {}
        with self.assertRaisesRegexp(Exception, "custom_params attribute is empty"):
            _validate_custom_params(custom_params=custom_params)


class TestConfigurationRunner(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.resource_config = mock.MagicMock()
        self.api = mock.MagicMock()

        class TestedConfigurationRunner(ConfigurationRunner):
            def cli_handler(self):
                pass

            def file_system(self):
                pass

            def restore_flow(self):
                pass

            def save_flow(self):
                pass

        self.runner = TestedConfigurationRunner(logger=self.logger,
                                                resource_config=self.resource_config,
                                                api=self.api)

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of the all abstract methods"""
        class TestedClass(ConfigurationRunner):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with abstract methods "
                                                "cli_handler, file_system, restore_flow, save_flow"):
            TestedClass(logger=self.logger,
                        resource_config=self.resource_config,
                        api=self.api)

    @mock.patch("cloudshell.devices.runners.configuration_runner.time")
    def test_save_returns_destination_filename(self, time):
        """Check that method will return destination file name"""
        expected_res = "test_name-running-{}".format(time.strftime())
        folder_path = "test path"
        validated_path = "validated path"
        self.resource_config.name = "test name"
        self.runner.save_flow = mock.MagicMock()
        self.runner.get_path = mock.MagicMock(return_value=validated_path)
        self.runner._validate_configuration_type = mock.MagicMock()
        # act
        result = self.runner.save(folder_path=folder_path,
                                  configuration_type='running',
                                  vrf_management_name=None,
                                  return_artifact=False)
        # verify
        self.assertEqual(result, expected_res)

    @mock.patch("cloudshell.devices.runners.configuration_runner.OrchestrationSavedArtifact")
    def test_save_returns_orchestration_saved_artifact(self, orchestration_saved_artifact_class):
        """Check that method will return OrchestrationSavedArtifact instance"""
        folder_path = "test path"
        orchestration_saved_artifact = mock.MagicMock()
        orchestration_saved_artifact_class.return_value = orchestration_saved_artifact
        self.resource_config.name = "test name"
        self.runner.save_flow = mock.MagicMock()
        self.runner.get_path = mock.MagicMock()
        self.runner._validate_configuration_type = mock.MagicMock()
        # act
        result = self.runner.save(folder_path=folder_path,
                                  configuration_type='running',
                                  vrf_management_name=None,
                                  return_artifact=True)
        # verify
        self.assertEqual(result, orchestration_saved_artifact)

    def test_restore(self):
        """Check that method will execute restore_flow"""
        path = "test path"
        validated_path = mock.MagicMock()
        self.runner.restore_flow = mock.MagicMock()
        self.runner.get_path = mock.MagicMock(return_value=validated_path)
        self.runner._validate_configuration_type = mock.MagicMock()
        # act
        self.runner.restore(path=path,
                            configuration_type="running",
                            restore_method="override",
                            vrf_management_name=None)
        # verify
        self.runner.restore_flow.execute_flow.assert_called_once_with(
            configuration_type="running",
            path=validated_path,
            restore_method="override",
            vrf_management_name=self.resource_config.vrf_management_name)
        self.runner.get_path.assert_called_once_with(path)
        self.runner._validate_configuration_type.assert_called_once_with("running")

    @mock.patch("cloudshell.devices.runners.configuration_runner.OrchestrationSaveResult")
    @mock.patch("cloudshell.devices.runners.configuration_runner.serialize_to_json")
    def test_orchestration_save(self, serialize_to_json, orchestration_saved_result_class):
        """Check that method will return serialized to json OrchestrationSaveResult object"""
        custom_params = "{}"
        self.runner.get_path = mock.MagicMock()
        self.runner.save = mock.MagicMock()
        self.runner._validate_artifact_info = mock.MagicMock()
        expected_res = mock.MagicMock()
        orchestration_saved_result = mock.MagicMock()
        serialize_to_json.return_value = expected_res
        orchestration_saved_result_class.return_value = orchestration_saved_result
        # act
        result = self.runner.orchestration_save(mode="test mode",
                                                custom_params=custom_params)
        # verify
        self.assertEqual(result, expected_res)
        serialize_to_json.assert_called_once_with(orchestration_saved_result)

    @mock.patch("cloudshell.devices.runners.configuration_runner.JsonRequestDeserializer")
    @mock.patch("cloudshell.devices.runners.configuration_runner._validate_custom_params")
    def test_orchestration_restore(self, _validate_custom_params, json_request_deserializer_class):
        """Check that method will call internal "restore" method with correct arguments"""
        custom_params = "{}"
        artifact_info = '{"saved_artifacts_info": {}}'
        self.runner.restore = mock.MagicMock()
        self.runner._validate_artifact_info = mock.MagicMock()
        parsed_artifact_info = mock.MagicMock()
        parsed_artifact_info.saved_artifacts_info.restore_rules.requires_same_resource = False
        json_request_deserializer_class.return_value = parsed_artifact_info

        # act
        self.runner.orchestration_restore(saved_artifact_info=artifact_info,
                                          custom_params=custom_params)
        # verify
        self.runner.restore.assert_called_once_with(
            configuration_type=parsed_artifact_info.custom_params.configuration_type,
            restore_method=parsed_artifact_info.custom_params.restore_method,
            vrf_management_name=parsed_artifact_info.custom_params.vrf_management_name,
            path="{}:{}".format(parsed_artifact_info.saved_artifacts_info.saved_artifact.artifact_type,
                                parsed_artifact_info.saved_artifacts_info.saved_artifact.identifier))

    def test_orchestration_restore_with_empty_saved_artifact_info(self):
        """Check that method will raise Exception if "saved_artifacts_info" argument is empty"""
        custom_params = "{}"
        artifact_info = ""
        # act
        with self.assertRaisesRegexp(Exception, "saved_artifact_info is None or empty"):
            self.runner.orchestration_restore(saved_artifact_info=artifact_info,
                                              custom_params=custom_params)

    def test_orchestration_restore_with_missed_artifact_info(self):
        """Check that method will raise Exception if there is no "saved_artifacts_info" attr"""
        custom_params = "{}"
        artifact_info = "{}"
        # act
        with self.assertRaisesRegexp(Exception, "Saved_artifacts_info is missing"):
            self.runner.orchestration_restore(saved_artifact_info=artifact_info,
                                              custom_params=custom_params)

    @mock.patch("cloudshell.devices.runners.configuration_runner.UrlParser")
    def test_get_path(self, url_parser_class):
        """Check that method will return UrlParser.build_url() result"""
        path = "some path"
        url = {
            url_parser_class.SCHEME: 'ftp'
        }
        url_parser_class.parse_url.return_value = url
        builded_url = mock.MagicMock()
        url_parser_class.build_url.return_value = builded_url
        # act
        result = self.runner.get_path(path=path)
        # verify
        self.assertEqual(result, builded_url)
        url_parser_class.parse_url.assert_called_once_with(path)

    @mock.patch("cloudshell.devices.runners.configuration_runner.UrlParser")
    def test_get_path_with_empty_path(self, url_parser_class):
        """Check that method will use backup location and backup type if path argument is missing"""
        self.resource_config.backup_location = "backup_location"
        self.resource_config.backup_type = "backup_type"
        url = mock.MagicMock()
        url_parser_class.build_url.return_value = url
        # act
        result = self.runner.get_path()
        # verify
        url_parser_class.parse_url.assert_called_once_with("backup_type://backup_location")

    @mock.patch("cloudshell.devices.runners.configuration_runner.UrlParser")
    def test_get_path_failed_to_build_url(self, url_parser_class):
        """Check that method will raise Exception if it unable to build the URL"""
        url_parser_class.build_url.side_effect = Exception
        # act
        with self.assertRaisesRegexp(Exception, "Failed to build path url to remote host"):
            self.runner.get_path(path="some path")

    def test_validate_configuration_type(self):
        """Check that method will raise Exception if configuration_type is not "startup" or "running" """
        with self.assertRaisesRegexp(Exception, "Configuration Type is invalid"):
            self.runner._validate_configuration_type(configuration_type="incorrect configuration type")

    def test_validate_artifact_info_missing_attr(self):
        """Check that method will raise Exception if there is no required attribute in the config object"""
        config = {}
        required_attr = "test_required_attr"
        self.runner.REQUIRED_SAVE_ATTRIBUTES_LIST = [required_attr]

        # verify
        with self.assertRaisesRegexp(Exception, "Mandatory field {} is missing in Saved Artifact Info "
                                                "request json".format(required_attr)):
            self.runner._validate_artifact_info(saved_config=config)

    def test_validate_artifact_info_missing_nested_attr(self):
        """Check that method will raise Exception if there is no required nested attribute in the config object"""
        config = mock.MagicMock(test_required_attr={})
        required_attr = "nested_attr"
        self.runner.REQUIRED_SAVE_ATTRIBUTES_LIST = [("test_required_attr", required_attr)]
        # verify
        with self.assertRaisesRegexp(Exception, "Mandatory field {} is missing in Saved Artifact Info "
                                                "request json".format(required_attr)):
            self.runner._validate_artifact_info(saved_config=config)

    @mock.patch("cloudshell.devices.runners.configuration_runner.OrchestrationRestoreRules")
    def test_get_restore_rules(self, orchestration_restore_rules_class):
        """Check that method will return OrchestrationRestoreRules instance"""
        orchestration_restore_rules = mock.MagicMock()
        orchestration_restore_rules_class.return_value = orchestration_restore_rules
        # act
        result = self.runner.get_restore_rules()
        # verify
        self.assertEqual(result, orchestration_restore_rules)
        orchestration_restore_rules_class.assert_called_once_with(True)
