class SubmissionProcessor:
    def __init__(self, auto_submission):
        self._auto_submission = auto_submission

    def process(self, api):
        if not self._auto_submission:
            return

        task = api.get_task()

        if task['status'] == 'Draft':
            print('Submitting task')
            api.submit_task()
        else:
            print('Task already submitted')
