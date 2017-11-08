# encoding=utf8
# author=spenly
# mail=i@spenly.com

from abc import ABCMeta, abstractclassmethod, abstractstaticmethod


class BaseClient(metaclass=ABCMeta):
    TYPE = "NTF"  # 'TF' or 'NTF', need TensorFlow or not

    @abstractclassmethod
    def prepare(self):
        """
        finish preparation work here
        need rewrite
        :return:
        """
        pass

    @abstractclassmethod
    def is_ready(self):
        """
        check here before run
        need rewrite
        :return: True or False
        """
        pass

    def preprocess(self, data):
        """
        preprocessing work
        :param data: data
        :return: data after preprocessing
        """
        return data

    @abstractclassmethod
    def run_model(self, data):
        """
        run model
        need rewrite
        :param data: data
        :return: return result
        """
        return data

    def postprocess(self, result):
        """
        postprocessing
        :param result: result
        :return: result
        """
        return result

    def run(self, data):
        """
        run function
        :param data: data
        :return: data
        """
        data = self.preprocess(data)
        result = self.run_model(data)
        return self.postprocess(result)

    @abstractclassmethod
    def docstring(self):
        """
        docstring for run function
        need rewrite
        :return: docstring
        """
        docs = """
        input:
        output:
        """
        return docs
