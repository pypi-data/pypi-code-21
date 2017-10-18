import os
from .. import utils
from .launcher import Launcher
from ..errors import InputError


class NerscSerialLauncher(Launcher):

    def generate(self, script_name):
        self._check_inputs()
        # Generate a bash script to run the pipeline locally under docker
        # Assume stages all built already
        lines = ['#!/bin/sh', 'set -e']

        for stage_name, stage_class in self.pipeline.sequence():
            lines += self._script_for_stage(stage_name, stage_class)


        lines.append("mkdir -p {}".format(self.data_dir()))
        lines.append("\n\n")
        for stage_name, stage_class in self.pipeline.sequence():
            lines.append("run_{}".format(stage_name))


        lines.append("\n### Now pipeline is complete. Copy results out. ###\n".format(stage_name))

        lines.append("mkdir -p {}".format(self.output_dir()))
        # Final copy out of results
        line = """
if [ ! -z "$(ls -A {data_dir})" ];
then
    mv {data_dir}/* {output_dir}/
fi
    """.format(data_dir=self.data_dir(), output_dir=self.output_dir())
        lines.append(line)
        lines.append("\n")

        with open(script_name, 'w') as script:
            script.write('\n'.join(lines))
        utils.make_user_executable(script_name)



    def working_dir(self):
        return self.info['working']        

    def data_dir(self):
        return os.path.join(self.working_dir(), "data")


    def _task_dirs(self, stage_name):
        stage_dir = os.path.join(self.working_dir(), stage_name)
        input_dir  = os.path.join(stage_dir, 'input')
        output_dir = os.path.join(stage_dir, 'output')
        config_dir = os.path.join(stage_dir, 'config')
        return input_dir, output_dir, config_dir

    def _input_path(self, input_tag, input_type):
        path = self.info['inputs'].get(input_tag)

        if path is None:
            path = os.path.join(self.data_dir(), input_tag+"."+input_type)

        return path


    def _script_for_stage(self, stage_name, stage_class):
        lines = ["\n### Run pipeline stage {} ###\n".format(stage_name), "function run_{} {{".format(stage_name)]

        input_dir, output_dir, config_dir = self._task_dirs(stage_name)
        lines.append("echo Running pipeline stage: {}".format(stage_name))

        lines.append("# Make working directories")
        lines.append("mkdir -p {}".format(input_dir))
        lines.append("mkdir -p {}".format(output_dir))
        lines.append("mkdir -p {}".format(config_dir))
        lines.append("")
        lines.append("# Make output directory")
        lines.append("mkdir -p {}".format(self.output_dir()))
        lines.append("")

        lines.append("# Hard link configuration files")
        for config_tag, config_filename in stage_class.config.items():
            filename = self.pipeline.cfg[stage_name]['config'][config_tag]
            path = os.path.join(self.config_dir(), filename)
            task_path = task_path = os.path.join(config_dir, config_filename)
            lines.append("cp {} {}".format(path, task_path))


        lines.append("# Hard link input files either from pipeline inputs or other module outputs")
        for input_tag, input_type in stage_class.inputs.items():
            path = self._input_path(input_tag, input_type)
            task_filename = "{}.{}".format(input_tag, input_type)
            task_path = os.path.join(input_dir, task_filename)
            lines.append("cp {} {}".format(path, task_path))

        image = self.pipeline.image_name(stage_name)
        input_mount = "-V {}:/opt/input".format(os.path.abspath(input_dir))
        output_mount = "-V {}:/opt/output".format(os.path.abspath(output_dir))
        config_mount = "-V {}:/opt/config".format(os.path.abspath(config_dir))

        lines.append("")
        lines.append("# Run the image")
        lines.append("")
        line ="shifter --image=docker:{} {} {} {} bash -lc /opt/desc/run.py".format(image, input_mount, output_mount, config_mount)
        lines.append(line)
        lines.append("")

        for output_tag, output_type  in stage_class.outputs.items():
            output_filename = "{}.{}".format(output_tag, output_type)
            task_path = os.path.join(output_dir, output_filename)
            data_path = os.path.join(self.data_dir(), output_filename)
            lines.append("cp {} {}".format(task_path, data_path))
        lines[2:] = utils.indent(lines[2:])
        lines.append("}\n\n\n")

        return lines



    def _check_inputs(self):
        inputs = self.pipeline.input_tags()
        for tag in inputs:
            path = self.info['inputs'].get(tag)
            if path is None:
                raise InputError("No path for input {} is specified in the pipeline file".format(tag))
            if not os.path.exists(path):
                raise InputError("Nothing found at specified input path: {}".format(path))
            if not os.path.isfile(path):
                raise InputError("Input path is a directory (not allowed): {}".format(path))


