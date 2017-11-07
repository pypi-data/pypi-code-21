import os
from locust import HttpLocust, TaskSet, task
from httprunner import utils, runner, exception

# define a class object (your class may be more complicated than this...)
# class A(object):
#     pass

# class WebPageUser(HttpLocust):
#     host = 'http://www.skypixel.com'
#     # task_set = WebPageTasks
#     min_wait = 1000
#     max_wait = 5000


class WebPageTasks(TaskSet):
    def on_start(self):
        self.test_runner = runner.Runner(self.client)
        self.testset = self.locust.testset

    @task
    def test_specified_scenario(self):
        try:
            self.test_runner._run_testset(self.testset)
        except exception.ValidationError:
            pass

print('WebPageTasks====1', dir(WebPageTasks), WebPageTasks.on_start)


def on_start(self):
    self.test_runner = runner.Runner(self.client)
    self.testset = self.locust.testset


def clsmethod(cls):
    print('clsmethod------', cls)


def clsmethod2(cls):
    print('clsmethod2------', cls)


WebPageTasks = type('WebPageTasks', (TaskSet,), {})

setattr(WebPageTasks, 'on_start', on_start)
setattr(WebPageTasks, 'clsmethod', clsmethod)
WebPageTasks.clsmethod2 = classmethod(clsmethod2)

print('WebPageTasks====2', WebPageTasks.__dict__)

print('3--------------', WebPageTasks().clsmethod(), WebPageTasks.clsmethod2())


testcase_file_path = os.path.join(os.getcwd(), 'skypixel.yml')
testsets = testcase.load_testcases_by_path(testcase_file_path)
testset = testsets[0]

variables_dict = {
    'host': 'http://www.skypixel.com',
    'task_set': WebPageTasks,
    'min_wait': 1000,
    'max_wait': 5000,
    'testset': testset
}

WebPageUser = type('WebPageUser', (HttpLocust,), variables_dict)

# print('WebPageUser-------', dir(WebPageUser), WebPageUser.testset)

# a class method takes the class object as its first variable
def func(cls):
    print('I am a class method')

A = type('A', (object,), {'func': func})

# you can just add it to the class if you already know the name you want to use
A.func = classmethod(func)

# or you can auto-generate the name and set it this way
the_name = 'other_func'
setattr(A, the_name, classmethod(func))

# print(dir(A))
print(A.func())
print(A.other_func())
