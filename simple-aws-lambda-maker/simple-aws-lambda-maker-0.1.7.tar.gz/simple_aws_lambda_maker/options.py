from simple_aws_lambda_maker.formatter import MergedOptionStringFormatter

from input_algorithms import spec_base as sb
from input_algorithms.dictobj import dictobj
from option_merge import MergedOptions
from contextlib import contextmanager
import tempfile
import zipfile
import os

class Salm(dictobj.Spec):
    config = dictobj.Field(sb.file_spec, wrapper=sb.optional_spec)
    dry_run = dictobj.Field(sb.boolean, default=False)
    task = dictobj.Field(sb.string_spec, default="help")
    group = dictobj.Field(sb.string_spec, wrapper=sb.optional_spec)

class SkillTrigger(dictobj.Spec):
    @property
    def sid(self):
        return "alexa_skill"

    @property
    def principal(self):
        return "alexa-appkit.amazon.com"

    def policy_statement(self, arn):
        sid = self.sid
        effect = "Allow"
        principal = {"Service": self.principal}
        action = "lambda:InvokeFunction"
        ret = {"Sid": sid, "Effect": effect, "Principal": principal, "Action": action}
        if arn is not None:
            ret["Resource"] = arn
        return ret

    def permissions(self, arn):
        return {"FunctionName": arn, "StatementId": self.sid, "Action": "lambda:InvokeFunction", "Principal": self.principal}

class SmartHomeTrigger(dictobj.Spec):
    sid = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)
    skill_identifier = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)

    @property
    def principal(self):
        return "alexa-connectedhome.amazon.com"

    def policy_statement(self, arn):
        sid = self.sid
        effect = "Allow"
        principal = {"Service": self.principal}
        action = "lambda:InvokeFunction"
        condition = {"StringEquals": {"lambda:EventSourceToken": self.skill_identifier}}
        ret = {"Sid": sid, "Effect": effect, "Principal": principal, "Action": action, "Condition": condition}
        if arn is not None:
            ret["Resource"] = arn
        return ret

    def permissions(self, arn):
        return {"FunctionName": arn, "StatementId": self.sid, "Action": "lambda:InvokeFunction", "Principal": self.principal, "EventSourceToken": self.skill_identifier}

class GatewayTrigger(dictobj.Spec):
    sid = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)
    gateway_identifier = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)

    @property
    def principal(self):
        return "apigateway.amazonaws.com"

    def policy_statement(self, arn):
        sid = self.sid
        effect = "Allow"
        principal = {"Service": self.principal}
        action = "lambda:InvokeFunction"
        condition = {'ArnLike': {'AWS:SourceArn': self.gateway_identifier}}
        ret = {"Sid": sid, "Effect": effect, "Principal": principal, "Action": action, "Condition": condition}
        if arn is not None:
            ret["Resource"] = arn
        return ret

    def permissions(self, arn):
        return {"FunctionName": arn, "StatementId": self.sid, "Action": "lambda:InvokeFunction", "Principal": self.principal, "SourceArn": self.gateway_identifier}

class trigger_spec(sb.Spec):
    def __init__(self):
        self.gateway_trigger_spec = GatewayTrigger.FieldSpec(formatter=MergedOptionStringFormatter)
        self.skill_trigger_spec = SkillTrigger.FieldSpec(formatter=MergedOptionStringFormatter)
        self.smart_home_trigger_spec = SmartHomeTrigger.FieldSpec(formatter=MergedOptionStringFormatter)

    def normalise_filled(self, meta, val):
        typ = sb.set_options(type=sb.required(sb.string_choice_spec(["alexa_skill", "alexa_smart_home", "gateway"]))).normalise(meta, val)["type"]
        if typ == "gateway":
            return self.gateway_trigger_spec.normalise(meta, val)
        elif typ == "alexa_smart_home":
            return self.smart_home_trigger_spec.normalise(meta, val)
        elif typ == "alexa_skill":
            return self.skill_trigger_spec.normalise(meta, val)

class Function(dictobj.Spec):
    filepath = dictobj.Field(format_into=sb.filename_spec, wrapper=sb.required)
    region = dictobj.Field(format_into=sb.string_spec, wrapper=sb.required)
    name = dictobj.Field(format_into=sb.string_spec, wrapper=sb.required)
    triggers = dictobj.Field(sb.listof(trigger_spec()))
    env = dictobj.Field(sb.dictof(sb.string_spec(), sb.formatted(sb.string_spec(), formatter=MergedOptionStringFormatter)))
    role = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)
    timeout = dictobj.Field(format_into=sb.integer_spec(), wrapper=sb.required)
    handler = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)
    runtime = dictobj.Field(format_into=sb.string_spec(), wrapper=sb.required)
    description = dictobj.Field(format_into=sb.string_spec(), default="")
    memory_size = dictobj.Field(format_into=sb.integer_spec(), default=128)
    tags = dictobj.Field(sb.dictof(sb.string_spec(), sb.formatted(sb.string_spec(), formatter=MergedOptionStringFormatter)))

    @contextmanager
    def code_options(self):
        with self.zipfile() as location:
            yield {"ZipFile": open(location, 'rb').read()}

    @contextmanager
    def zipfile(self):
        with tempfile.NamedTemporaryFile(suffix=".zip") as fle:
            with open(self.filepath) as code:
                with zipfile.ZipFile(fle.name, "w") as zf:
                    zf.write(code.name, os.path.basename(self.filepath))
            yield fle.name

    def policy_statement(self, arn):
        return [t.policy_statement(arn) for t in self.triggers]

    @property
    def configuration(self):
        return dict(
              FunctionName = self.name
            , Runtime = self.runtime
            , Role = self.role
            , Handler = self.handler
            , Description = self.description
            , Timeout = self.timeout
            , MemorySize = self.memory_size
            , Publish = False
            , Environment = {"Variables": self.env }
            , Tags = self.tags
            )

class function_spec(sb.Spec):
    def __init__(self):
        self.spec = Function.FieldSpec(formatter=MergedOptionStringFormatter)

    def normalise_filled(self, meta, val):
        val = MergedOptions.using(meta.everything.get("function_defaults", {}), val)
        return self.spec.normalise(meta, val)
