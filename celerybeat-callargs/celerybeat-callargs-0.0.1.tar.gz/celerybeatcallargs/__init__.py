from celery.beat import Scheduler


class CallableArgsScheduler(Scheduler):

    def setup_schedule(self):
        super().setup_schedule()
        self.merge_inplace(self.app.conf.beat_schedule)

    def apply_entry(self, entry, producer=None):
        entry.args = tuple(map(lambda x: x() if callable(x) else x,
                               entry.args))
        entry.kwargs = {k: (v() if callable(v) else v)
                        for k, v in entry.kwargs.items()}
        super().apply_entry(entry, producer)

    @property
    def info(self):
        return "    . non-persistent schedule"
