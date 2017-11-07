import inspect
import logging

from jsonschema import validate, ValidationError

from .. import func_loading
from ..errors import ExtractorError
from ..parsers import JSONParser, JSONPathParser


class FeatureFromJsonExtractor(object):
    """ 特征抽取器，从json数据中抽取，返回特征向量

    Parameters

    json_parser_cls : class
        解析json path的解析类，继承自``JSONParser``

    Attributes


    Examples

    >>> from velenxc.preprocessing.extract import FeatureFromJsonExtractor
    >>> extractor = FeatureFromJsonExtractor()
    >>> feature_vector = extractor.transform({...}, [...])

    """
    json_parser_cls = JSONPathParser
    func_pipeline_separator = '->'

    config_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string"},
                "cn_name": {"type": "string"},
                "jsonpath": {"type": "array"},
                "func_chains": {"type": "string"},
                "parse_type": {"type": "string"}
            },
            "required": ["feature_name", "jsonpath"]
        },
    }

    def __init__(self, json_parser_cls=None,
                 func_pipeline_separator=None):

        if inspect.isclass(json_parser_cls) and \
                issubclass(json_parser_cls, JSONParser):
            self.json_parser_cls = json_parser_cls

        self.json_parser = self.json_parser_cls()

        if func_pipeline_separator:
            self.func_pipeline_separator = func_pipeline_separator

        self._execution_plan = []

    @classmethod
    def schema_valid(cls, json, schema):
        if schema:
            try:
                validate(json, schema)
            except ValidationError as ve:
                logging.error("Validation Error: {0}".format(ve))
                raise ExtractorError("Feature config is not valid, please check them")

    def transform_one_feature(self, data, config):
        """ 计算一个特征 """
        json_paths = config.get('jsonpath')

        parse_result = self.json_parser.parse(
            data, json_paths, **{'parse_type': config.get('parse_type')}
        )

        func_chains = config.get('func_chains')
        self._execution_plan = self.make_execution_plan(func_chains)

        # 从函数库里加载func_name, 函数库包括两部分
        feature_value = parse_result.get('parse_values')
        if feature_value == [None]:
            return None

        for plan in self._execution_plan:
            func_name = plan.get('func_name')
            args = plan.get('args')

            func = func_loading.import_function(func_name)
            if args:
                feature_value = func(feature_value, *args)
            elif func:
                feature_value = func(feature_value)

        if isinstance(feature_value, list):
            if len(feature_value) > 0:
                feature_value = feature_value[0]
            else:
                feature_value = None

        return feature_value

    def make_execution_plan(self, func_chains):
        """ 生成执行计划 """
        plan = []

        if not func_chains:
            return plan

        func_chains = func_chains.strip().split(self.func_pipeline_separator)
        for func_sign in func_chains:
            plan.append(self.parse_func_sign(func_sign))

        return plan

    @classmethod
    def parse_func_sign(cls, func_sign):
        """ 解析函数签名字符串 """
        func_name = func_sign
        args = None

        if '(' in func_sign and func_sign.endswith(')'):
            left_bracket_index = func_sign.find('(')
            args = func_sign[left_bracket_index + 1:-1]

            def _parameter(args_sign):
                args_sign = args_sign.strip()

                if not args_sign.startswith('"') and not args_sign.startswith("'"):
                    if "." in args_sign:
                        args_sign = float(args_sign)
                    else:
                        args_sign = int(args_sign)
                else:
                    args_sign = args_sign.strip("'").strip('"')

                return args_sign

            args = map(_parameter, args.split(','))
            func_name = func_sign[:left_bracket_index]

        return {
            'func_name': func_name,
            'args': args
        }

    def transform(self, data, configs):
        """ 在数据上应用配置，产生特征向量

        * Parameters

        data : dict or list, default=None
            json数据，抽取特征使用

        configs : list
            feature的配置列表，每一项的配置项如下：
            ``feature_name``
            ``cn_name``
            ``jsonpath`` : list
            ``func_chains``
            ``parse_type``

        * Return

        :raise ``velenxc.errors.ExtractorError``
        """
        feature_vector = {}

        self.schema_valid(configs, self.config_schema)

        for feature_config in configs:
            feature_name = feature_config.get('feature_name')
            try:
                feature_vector.update({
                    feature_name: self.transform_one_feature(data, feature_config)
                })
            except Exception as e:
                logging.error("feature_name:%s Exception:%s", feature_name, e.args, exc_info=True)
                feature_vector.update({feature_name: 'ERROR'})

        self.schema_valid(feature_vector, None)

        return feature_vector
