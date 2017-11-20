# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .resources import VALID_PARAMS, SGE, GE, SLURM, LSF


class BaseSystem(object):
    __metaclass__ = ABCMeta

    def __str__(self):
        return self.__class__.__name__

    @staticmethod
    def _prepare_resources(res, res_map):
        output = []

        for name in VALID_PARAMS:
            if name in res:
                output.append(res_map[name].format(res[name]))

        return ' '.join(output)

    def is_slurm(self):
        return False

    def is_sge(self):
        return False

    def is_lsf(self):
        return False

    @abstractmethod
    def native_resources(self, resources):
        if self.is_sge() and SGE in resources:
            return resources[SGE]
        elif self.is_sge() and GE in resources:
            return resources[GE]
        elif self.is_slurm() and SLURM in resources:
            return resources[SLURM]
        elif self.is_lsf() and LSF in resources:
            return resources[LSF]
        else:
            return resources


class SystemSGE(BaseSystem):
    def is_sge(self):
        return True

    def native_resources(self, resources):
        res = super(SystemSGE, self).native_resources(resources)
        # On SGE memory needs to be provided per/slot or core
        if "mem" in res:
            cpu = res.get("cpu", 1)
            res["mem"] = int(res["mem"] / cpu)

        res_map = {
            "cpu": "-pe smp {0}",
            "mem": "-l h_vmem={0}M",
            "queue": "-q {0}",
            "custom": "{0}",
        }
        return self._prepare_resources(res, res_map)


class SystemLSF(BaseSystem):
    def is_lsf(self):
        return True

    def native_resources(self, resources):
        res = super(SystemLSF, self).native_resources(resources)
        res_map = {
            "cpu": "-n {0}",
            "mem": '-M {0} -R "select[(mem>={0})] rusage[mem={0}] span[hosts=1]"',
            "queue": "-q {0}",
            "custom": "{0}",
        }
        return self._prepare_resources(res, res_map)


class SystemSLURM(BaseSystem):
    def is_slurm(self):
        return True

    def native_resources(self, resources):
        res = super(SystemSLURM, self).native_resources(resources)
        # On SLURM mem needs to be provided per CPU and we use MB so mem can be an integer
        if "mem" in res:
            cpu = res.get("cpu", 1)
            res["mem"] = int(res["mem"] / cpu)

        res_map = {
            "cpu": "--cpus-per-task={0} --nodes=1",
            "mem": "--mem-per-cpu={0}",
            "queue": "--partition={0}",
            "custom": "{0}",
        }
        return self._prepare_resources(res, res_map)


# vim: ai sts=4 et sw=4
