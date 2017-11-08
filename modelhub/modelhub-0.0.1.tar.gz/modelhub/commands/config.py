# -*- coding: utf-8 -*-
from .base import BaseCommand, option, argument, register   # noqa
from modelhub.core import conf, utils


@register("config")
class Command(BaseCommand):

    arguments = []

    params = {
        "user_name": "Your Name",
        "user_email": "Your Email",
        "local_data_dir": "Path of data dir",
        "aws_access_key_id": "AWS ACCESS_KEY_ID",
        "aws_secret_access_key": "AWS SECRET_ACCESS_KEY",
        "aws_region_name": "AWS REGION_NAME",
        "aws_bucket_name": "AWS BUCKET_NAME",
        "aws_base_path": "AWS BASE_PATH",
    }

    interactive_keys = [
        "user_name",
        "user_email",
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_region_name",
        "aws_bucket_name",
    ]

    @classmethod
    def add_arguments(cls):
        return super().add_arguments() + [
            option("-i", "--interactive", is_flag=True, help="Enter interactive mode")
        ] + [
            option(
                "--" + key.replace(".", "_"),
                help=help_text
            )
            for key, help_text in cls.params.items()
        ]

    def run(self, interactive=True, **kwargs):
        "Get and set modelhub global options"
        values = {k: v for k, v in kwargs.items() if v}
        input_keys = set(values)
        if interactive:
            for k in self.interactive_keys:
                if k in input_keys:
                    continue
                current_value = values.get(k) or getattr(conf, k.upper(), None)
                new_value = self.get_input(k, current_value)
                values[k] = new_value

        if values:
            values = {k: v for k, v in values.items() if v != getattr(conf, k.upper(), None)}
            if values:
                self.write_config(values)
        else:
            self.show_config()

    def write_config(self, v):
        utils.write_conf(conf.RC_PATH, **v)
        print("saved to {path}".format(path=conf.RC_PATH))
        for key, value in v.items():
            print("{key}:\t{value}".format(key=key, value=value))

    def get_input(self, k, v):
        help_text = "%s:" % self.params[k]
        if v:
            help_text += "[%s]" % v
        help_text += ">>"
        new_v = input(help_text).strip()

        return new_v or v

    def show_config(self):
        for k, help_text in self.params.items():
            print("{help_text}({key}):\n    {value}\n".format(
                key=k,
                help_text=help_text,
                value=getattr(conf, k.upper()))
            )
