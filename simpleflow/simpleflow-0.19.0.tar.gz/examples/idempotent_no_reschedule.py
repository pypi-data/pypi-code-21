from simpleflow import activity, Workflow, futures


@activity.with_attributes(task_list="example",
                          version="example",
                          idempotent=True)
def identity(x):
    return x


class BasicWorkflow(Workflow):
    name = "basic"
    version = "example"
    task_list = "example"

    def run(self, x):
        y = self.submit(identity, x)
        z = self.submit(identity, 5)
        futures.wait(z)
        t = self.submit(identity, y.result)
        return t.result
