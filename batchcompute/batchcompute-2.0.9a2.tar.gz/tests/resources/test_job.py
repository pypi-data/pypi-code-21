import unittest

from batchcompute.resources.job import *
from batchcompute.resources import Configs

class JobDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.oss_path = "oss://xxxx/xxxx"
        self.cmdline = "echo Batchcompute"
        self.instance_count = 10
        self.timeout = 1000

        self.job_name = "Batchcompute"
        self.job_description = "Job created by Python SDK"
        self.priority = 100
        self.fail_depend_on_instance = True

    def get_inputmapping(self):
        cfg = InputMappingConfig(dict())

        self.assertEqual(cfg.Locale, "GBK")
        self.assertEqual(cfg.Lock, False)

        cfg = InputMappingConfig()
        locale = 'GBK'
        lock = True

        cfg.Locale = locale
        cfg.Lock = lock 

        self.assertEqual(cfg.Locale, locale)
        self.assertEqual(cfg.Lock, lock)

        return cfg

    def get_command(self):
        cmd = Command()

        cmd.CommandLine = self.cmdline 
        cmd.PackagePath = self.oss_path 
        cmd.EnvVars = {} 

        self.assertEqual(cmd.CommandLine, self.cmdline)
        self.assertEqual(cmd.PackagePath, self.oss_path)
        self.assertEqual(cmd.EnvVars, {})
        return cmd

    def get_parameters(self):
        cfg = self.get_inputmapping()
        cmd = self.get_command()

        par = Parameters()
        par.Command = cmd
        par.InputMappingConfig = cfg
        par.StdoutRedirectPath = self.oss_path 
        par.StderrRedirectPath = self.oss_path 

        self.assertTrue(par.StdoutRedirectPath, self.oss_path)
        self.assertTrue(par.StderrRedirectPath, self.oss_path)

        return par

    def get_task_description(self):
        par = self.get_parameters()

        task_desc = TaskDescription()
        task_desc.Parameters = par
        task_desc.InstanceCount = self.instance_count 
        task_desc.Timeout = self.timeout 

        self.assertEqual(task_desc.Parameters.dump(), par.dump())
        self.assertEqual(task_desc.InstanceCount, self.instance_count)
        self.assertEqual(task_desc.Timeout, self.timeout)

        self.assertEqual(task_desc.InputMapping, dict())
        self.assertEqual(task_desc.OutputMapping, dict())
        self.assertEqual(task_desc.LogMapping, dict())

        return task_desc

    def get_dag(self):
        dag = DAG()

        task1 = self.get_task_description()
        task2 = self.get_task_description()
        task3 = self.get_task_description()

        dag.add_task('task1', task1)
        dag.add_task('task2', task2)
        dag.add_task('task3', task3)

        self.assertEqual(dag.get_task('task1').dump(), task1.dump())
        self.assertEqual(dag.get_task('task2').dump(), task2.dump())
        self.assertEqual(dag.get_task('task3').dump(), task3.dump())

        dag.delete_task('task1')
        dag.delete_task('task2')
        dag.delete_task('task3')

        self.assertRaises(KeyError, dag.get_task, 'task1')

        self.assertEqual(dag.Dependencies, {})

        dag.add_task('task1', task1)
        dag.add_task('task2', task2)
        dag.add_task('task3', task3)

        return dag

    def get_job_description(self):
        dag = self.get_dag()

        job_desc = JobDescription()
        job_desc.Name = self.job_name
        job_desc.Priority = self.priority
        job_desc.JobFailOnInstanceFail = self.fail_depend_on_instance

        job_desc.DAG = dag

        self.assertEqual(job_desc.Type, "DAG")
        self.assertEqual(job_desc.Name, self.job_name)
        self.assertEqual(job_desc.Priority, self.priority)
        self.assertEqual(job_desc.JobFailOnInstanceFail, self.fail_depend_on_instance)
        self.assertEqual(job_desc.DAG.dump(), dag.dump())

        return job_desc

    def testCommand(self):
        self.get_command()

    def testParameters(self):
        self.get_parameters()

    def testInputMappingConfig(self):
        self.get_inputmapping()

    def testTaskDescription(self):
        self.get_task_description()

    def testDAG(self):
        self.get_dag()

    def testJobDescription(self):
        self.get_job_description()


if __name__ == '__main__':
    unittest.main()
