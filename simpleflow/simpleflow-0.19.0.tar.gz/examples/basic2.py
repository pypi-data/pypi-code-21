from simpleflow import activity, Workflow, futures


@activity.with_attributes(task_list='quickstart', version='example')
def increment(x):
    return x + 1


@activity.with_attributes(task_list='quickstart', version='example')
def double(x):
    return x * 2


class BasicWorkflow(Workflow):
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self, x):
        y = self.submit(increment, x)
        z = self.submit(double, y)

        print('({x} + 1) * 2 = {result}'.format(
            x=x, result=z.result))

        return z.result

