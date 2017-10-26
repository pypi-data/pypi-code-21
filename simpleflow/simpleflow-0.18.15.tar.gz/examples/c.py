from simpleflow import Workflow, futures

if False:
    from simpleflow.history import History


class CWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def before_replay(self, history):
        # type: (History) -> None
        # print(len(history.events))
        # print(history._history.last)
        have_completed_decisions = self.have_completed_decisions(history)
        print('Have Completed Decisions: {}'.format(have_completed_decisions))

    @staticmethod
    def have_completed_decisions(history):
        completed_decisions = history.swf_history.filter(type='DecisionTask', state='completed')
        try:
            next(completed_decisions)
            return True
        except StopIteration:
            return False

    def after_replay(self, history):
        # type: (History) -> None
        print('after_replay')

    def after_closed(self, history):
        # type: (History) -> None
        print('after_closed')

    def run(self, *args, **kwargs):
        print('run: start')
        futures.wait(
            self.submit(self.signal('signal1')),
            self.submit(self.wait_signal('signal1')),
        )
        print('run: end')
