from aiida.work.workchain import WorkChain
from aiida.orm.data.base import NumericType


class ZombieWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super(ZombieWorkChain, cls).define(spec)
        spec.output('out', valid_type=NumericType)
        spec.outline(cls._step1, cls._step2, cls._step3)
    def _step1(self):
        print 'I am a zombie'
    def _step2(self):
        raise Exception()
    def _step3(self):
        # This step is never reached
        pass

