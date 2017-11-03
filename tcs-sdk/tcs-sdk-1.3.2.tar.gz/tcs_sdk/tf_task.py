import logging
import subprocess
import tensorflow as tf
from tcs_sdk import storage
import traceback

logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


class TcsTFTask(object):
    storage_cls = storage.Storage

    def __init__(self, *args, **kwargs):
        # self.init_op = tf.global_variables_initializer()

        self.model_storage = self.storage_cls.from_str(kwargs.get("model_dst"))
        self.graph_storage = self.storage_cls.from_str(kwargs.get("graph_dst"))
        self.data_storage = self.storage_cls.from_str(kwargs.get("data_source"))

    def input(self):
        return self.data_storage.open()

    def train(self):
        # return tensorflow session
        raise NotImplementedError

    def on_failure(self, exception):
        print("Task %s failure:%s" % (self, exception))

    def on_success(self):
        print("Task %s succeed" % self)

    def output_graph(self, session):
        print("Saving Graph to ", self.graph_storage.path)
        file_writer = tf.summary.FileWriter(self.graph_storage.path, session.graph)
        file_writer.flush()
        file_writer.close()

    def output_model(self, session):
        print("Saving Model to ", self.model_storage.path)
        # saver = tf.train.Saver()
        # saver.save(session, self.model_storage.path)
        builder = tf.saved_model.builder.SavedModelBuilder(self.model_storage.path)
        builder.add_meta_graph_and_variables(session, [tf.saved_model.tag_constants.SERVING])
        builder.save()

    @staticmethod
    def from_task_cls(class_, *args, **kwargs):
        return class_(*args, **kwargs)


def load_task_cls(code_source):
    from importlib.machinery import SourceFileLoader
    store = storage.Storage.from_str(code_source)
    foo = SourceFileLoader("task", store.path).load_module()
    return getattr(foo, "MainTask")


def tf_flow(code_source, data_source, model_dst, graph_dst):
    task_cls = load_task_cls(code_source)
    if not task_cls:
        print("Task not found %s", code_source)
        raise RuntimeError("Task not found")

    task = TcsTFTask.from_task_cls(task_cls, data_source=data_source, model_dst=model_dst, graph_dst=graph_dst)

    try:
        print("**Segment**:: TASK Training...")
        session = task.train()
        print("**Segment**:: TASK output graph...")
        task.output_graph(session)
        print("**Segment**:: TASK save model ..")
        task.output_model(session)

        print("**Segment**:: TASK succeed ..")
        task.on_success()



    except Exception as e:
        task.on_failure(e)


def create_tensorboard(graph_storage):
    subprocess.run(["tensorboard", "--logdir=%s" % graph_storage.path])


def serve_tensforflow(model_storage):
    pass


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Tensorflow sdk ')
    parser.add_argument('--code-source', type=str)
    parser.add_argument('--data-source', type=str)
    parser.add_argument('--model-dst', type=str)
    parser.add_argument('--graph-dst', type=str)
    parser.add_argument('--task-type', type=str)

    args = parser.parse_args()
    print("Training Model Args:%s" % args)

    try:
        if args.task_type == 'train':
            tf_flow(args.code_source, args.data_source, args.model_dst, args.graph_dst)
        elif args.task_type == 'debug':
            create_tensorboard(args.graph_dst)
        else:
            print("TaskType unknown %s" % args.task_type)
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
