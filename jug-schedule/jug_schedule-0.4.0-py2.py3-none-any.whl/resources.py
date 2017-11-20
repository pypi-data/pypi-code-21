# -*- coding: utf-8 -*-

from jug.task import TaskGenerator

__all__ = [
    "ResourcesTaskGenerator",
]

VALID_PARAMS = ("cpu", "mem", "queue", "custom")
SGE = "SGE"
GE = "GE"
LSF = "LSF"
SLURM = "SLURM"
SYSTEMS = (SGE, GE, LSF, SLURM)


class _WrapTaskGenerator(TaskGenerator):
    def __init__(self, f, resources):
        super(_WrapTaskGenerator, self).__init__(f)
        self._resources = resources

    def __call__(self, *args, **kwargs):
        task = super(_WrapTaskGenerator, self).__call__(*args, **kwargs)
        task._resources = self._resources
        return task


def ResourcesTaskGenerator(**resources):
    """
    @ResourcesTaskGenerator(cpu=10, mem=100)
    def f(arg0, arg1, ...)
        ...

    Behaves the same as jug's TaskGenerator but allows specifying resources
    which will then be used by the scheduler on requests to the queueing
    system.

    Current list of supported arguments ::

        cpu    = Number of cpu cores/threads to allocate
        mem    = Maximum memory necessary (in MB)
        queue  = Name of queue to use
        custom = Arbitrary native specification options

    All of the above are optional.

    Also note that these arguments are ignored if running with 'jug execute'.
    They are only relevant when using 'jug schedule'

    Additionally you can define system specific resources by using:

    from jug_schedule.resources import SGE, SLURM

    specific_resources = {
        SLURM: {
            "queue": "hpc",
        },
        SGE: {
            "mem": 120,
        }
    }

    @SystemResourcesTaskGenerator(cpu=10, mem=100, **specific_resources)
    def f(arg0, arg1, ...)
        ...

    System specific resources take precedence. In the example above, jobs will
    use 120MB memory on SGE (Sun Grid Engine) and 100MB otherwise.

    Targets (SGE, SLURM, ...) should be imported from jug_schedule.resources
    """
    PARAMS = VALID_PARAMS + SYSTEMS

    for key in resources:
        assert key in PARAMS, "Invalid resource specified {0}".format(key)

        if key in SYSTEMS:
            for subkey in resources[key]:
                assert subkey in VALID_PARAMS, "Invalid resource specified {0} under {1}".format(subkey, key)

            # Transfer common settings to each specified system
            for param in VALID_PARAMS:
                # System specific settings take precedence
                if param in resources[key]:
                    continue

                setting = resources.get(param)

                if setting is not None:
                    resources[key][param] = setting

    def task_generator_wrapper(f):
        return _WrapTaskGenerator(f, resources)

    return task_generator_wrapper


# vim: ai sts=4 et sw=4
