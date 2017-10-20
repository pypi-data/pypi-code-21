# Third party imports
import pytest

# Local imports
from uplink import commands, utils


class TestHttpMethodFactory(object):

    def test_call_as_decorator_with_no_args(self):
        @commands.HttpMethodFactory(None)
        def func(): pass
        assert isinstance(func, commands.RequestDefinitionBuilder)

    def test_call_as_decorator_with_args(self):
        method_factory = commands.HttpMethodFactory(None)

        @method_factory(None)
        def func(): pass
        assert isinstance(func, commands.RequestDefinitionBuilder)


class TestHttpMethod(object):

    def test_call(self, mocker, annotation_mock):
        # Setup
        def func(): pass
        sig = utils.Signature(
            args=["self", "arg1", "arg2"],
            annotations={"arg1": annotation_mock},
            return_annotation=None
        )
        mocker.patch("uplink.utils.get_arg_spec").return_value = sig

        http_method = commands.HttpMethod("METHOD", uri="/{hello}")
        builder = http_method(func)
        assert isinstance(builder, commands.RequestDefinitionBuilder)
        assert builder.__name__ == func.__name__
        assert builder.method == "METHOD"
        assert list(builder.uri.remaining_variables) == ["hello"]

        missing_arguments = builder.argument_handler_builder.missing_arguments
        expected_missing = set(sig.args[1:]) - set(sig.annotations.keys())
        assert set(missing_arguments) == expected_missing


class TestURIDefinitionBuilder(object):

    def test_is_static(self):
        assert not commands.URIDefinitionBuilder(None).is_static

    def test_is_dynamic_setter(self):
        uri = commands.URIDefinitionBuilder(None)
        assert not uri.is_dynamic
        uri.is_dynamic = True
        assert uri.is_dynamic

    def test_is_dynamic_setter_fails_when_is_static(self):
        uri = commands.URIDefinitionBuilder(True)
        assert uri.is_static
        with pytest.raises(ValueError):
            uri.is_dynamic = True

    def test_remaining_variables(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        assert uri.remaining_variables == set(["variable"])

    def test_add_variable(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        assert "variable" in uri.remaining_variables
        uri.add_variable("variable")
        assert "variable" not in uri.remaining_variables

    def test_add_variable_raise_error_when_name_is_not_in_static_path(self):
        uri = commands.URIDefinitionBuilder("/static/path")
        with pytest.raises(ValueError):
            uri.add_variable("variable")

    def test_build(self):
        uri = commands.URIDefinitionBuilder("/static/path")
        assert uri.build() == "/static/path"

    def test_build_fails_when_variable_remain_in_uri(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        with pytest.raises(commands.MissingUriVariables):
            uri.build()


class TestRequestDefinitionBuilder(object):

    def test_method_handler_builder_getter(self,
                                           annotation_handler_builder_mock):
        builder = commands.RequestDefinitionBuilder(
            None,
            None,
            type(annotation_handler_builder_mock)(),
            annotation_handler_builder_mock
        )
        assert builder.method_handler_builder is annotation_handler_builder_mock

    def test_build(self,
                   mocker,
                   annotation_handler_builder_mock,
                   uplink_builder_mock
        ):
        argument_handler_builder = type(annotation_handler_builder_mock)()
        method_handler_builder = annotation_handler_builder_mock
        uri_definition_builder = mocker.Mock(spec=commands.URIDefinitionBuilder)
        builder = commands.RequestDefinitionBuilder(
            "method",
            uri_definition_builder,
            argument_handler_builder,
            method_handler_builder
        )
        definition = builder.build(uplink_builder_mock)
        assert isinstance(definition, commands.RequestDefinition)
        assert uri_definition_builder.build.called
        assert argument_handler_builder.build.called
        assert method_handler_builder.build.called


class TestRequestDefinition(object):
    def test_argument_annotations(self, annotation_handler_mock):
        annotation_handler_mock.annotations = ["arg1", "arg2"]
        definition = commands.RequestDefinition(
            None, None, annotation_handler_mock, None
        )
        assert list(definition.argument_annotations) == ["arg1", "arg2"]

    def test_method_annotations(self, annotation_handler_mock):
        annotation_handler_mock.annotations = ["arg1", "arg2"]
        definition = commands.RequestDefinition(
            None, None, None, annotation_handler_mock
        )
        assert list(definition.method_annotations) == ["arg1", "arg2"]

    def test_define_request(self, request_builder, mocker):
        method = "method"
        uri = "uri"
        definition = commands.RequestDefinition(
            method, uri, mocker.Mock(), mocker.Mock())
        definition.define_request(request_builder, (), {})
        assert request_builder.method == method
        assert request_builder.uri == uri
