import os
from dxpy.time.utils import now


class DeamonService:
    @classmethod
    def cycle(cls):
        from .service import auto_complete, auto_submit_chain, auto_submit_root, auto_start
        auto_complete()
        auto_submit_chain()
        auto_submit_root()
        auto_start()
        print('Cycle at {t}.'.format(t=now(True)))

    @classmethod
    def start(cls, cycle_intervel=None):
        from apscheduler.schedulers.blocking import BlockingScheduler
        scheduler = BlockingScheduler()
        scheduler.add_job(cls.cycle, 'interval', seconds=60)
        print(
            'Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            cls.cycle()
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

    @staticmethod
    def stop():
        raise NotImplementedError

    @staticmethod
    def restart():
        raise NotImplementedError

    @staticmethod
    def is_running():
        pass
