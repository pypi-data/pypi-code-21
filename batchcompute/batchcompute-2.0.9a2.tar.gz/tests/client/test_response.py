import unittest

from batchcompute.client.response import *


class ResponseTest(unittest.TestCase):
    def setUp(self):
        pass

    def get_group(self):
        group_dict = { 
            "DesiredVMCount": 3,
            "ActualVMCount": 2, 
            "InstanceType": "", 
            "ResourceType": "OnDemand"
        }

        group = Group(group_dict)

        self.assertEqual(group.DesiredVMCount, 3) 
        self.assertEqual(group.ActualVMCount, 2) 
        self.assertEqual(group.InstanceType, "") 
        self.assertEqual(group.ResourceType, "OnDemand") 
        
        return group.detail()

    def get_metrics(self):
        metric_dict = { 
            "RunningCount": 1,
            "StartingCount": 2, 
            "StoppingCount": 3, 
            "StoppedCount": 4,
        }

        metrics = Metrics(metric_dict)

        self.assertEqual(metrics.RunningCount, 1) 
        self.assertEqual(metrics.StartingCount, 2) 
        self.assertEqual(metrics.StoppingCount, 3) 
        self.assertEqual(metrics.StoppedCount, 4) 

        return metrics.detail()

    def get_cluster(self):
        cluster_dict = {
            "Name": "",
            "Id": "", 
            "OwnerId": 123, 
            "Description": "", 
            "CreationTime": "", 
            "State": "Active", 
            "ImageId": "", 
            "Groups": {
                "group1": self.get_group(),
                "group2": self.get_group(),
                "group3": self.get_group()
            },
            "OperationLogs": ["",""], 
            "Metrics": self.get_metrics() 
        }

        cluster = Cluster(cluster_dict)
        self.assertEqual(len(cluster.Groups.keys()), 3)
        return cluster.detail()

    def get_task_metrics(self):
        task_metric_dict = {
            "WaitingCount": 1, 
            "RunningCount": 1, 
            "FinishedCount": 1, 
            "FailedCount": 1, 
            "StoppedCount": 1 
        }

        task_metric = TaskMetrics(task_metric_dict)

        self.assertEqual(task_metric.WaitingCount, 1)
        self.assertEqual(task_metric.RunningCount, 1)
        self.assertEqual(task_metric.FinishedCount, 1)
        self.assertEqual(task_metric.FailedCount, 1)
        self.assertEqual(task_metric.StoppedCount, 1)

        return task_metric.detail()

    def get_instance_metrics(self):
        instance_metric_dict = {
            "WaitingCount": 1, 
            "RunningCount": 1, 
            "FinishedCount": 1, 
            "FailedCount": 1, 
            "StoppedCount": 1 
        }

        instance_metrics = TaskMetrics(instance_metric_dict)

        self.assertEqual(instance_metrics.WaitingCount, 1)
        self.assertEqual(instance_metrics.RunningCount, 1)
        self.assertEqual(instance_metrics.FinishedCount, 1)
        self.assertEqual(instance_metrics.FailedCount, 1)
        self.assertEqual(instance_metrics.StoppedCount, 1)

        return instance_metrics.detail()

    def get_job(self):
        job_dict = {
            "Name": "",
            "Id": "",
            "Owner": "", 
            "CreationTime": "", 
            "State": "", 
            "Message": "",
            "StartTime": "", 
            "EndTime": "", 
            "TaskMetrics": self.get_task_metrics(),
            "InstanceMetrics": self.get_instance_metrics()
        }

        job = Job(job_dict)

        self.assertEqual(job.Name, "")
        self.assertEqual(job.Id, "")
        self.assertEqual(job.Owner, "")
        self.assertEqual(job.State, "")
        self.assertEqual(job.Message, "")
        self.assertEqual(job.StartTime, "")
        self.assertEqual(job.EndTime, "")
        self.assertEqual(job.TaskMetrics.detail(), self.get_task_metrics())
        self.assertEqual(job.InstanceMetrics.detail(), self.get_instance_metrics())

        return job.detail()

    def get_task(self):
        task_dict = {
            "TaskName": "",
            "State": "", 
            "StartTime": "", 
            "EndTime": "", 
            "InstanceMetrics": self.get_instance_metrics()
        }

        task = Task(task_dict)

        self.assertEqual(task.TaskName, "")
        self.assertEqual(task.State, "")
        self.assertEqual(task.StartTime, "")
        self.assertEqual(task.EndTime, "")
        self.assertEqual(task.InstanceMetrics.detail(), self.get_instance_metrics())

        return task.detail()

    def get_image(self):
         
        image_dict = {
            "Name": "",
            "Id": "",
            "Description": "", 
            "CreationTime": "", 
            "OwnerId": "123",
            "Platform": "Windows", 
            "ECSImageId": "", 
        }

        image = Image(image_dict)

        self.assertEqual(image.Name, "")
        self.assertEqual(image.Id, "")
        self.assertEqual(image.Description, "")
        self.assertEqual(image.CreationTime, "")
        self.assertEqual(image.OwnerId, "123")
        self.assertEqual(image.Platform, "Windows")
        self.assertEqual(image.ECSImageId, "")
        return image.detail()

    def get_result(self):
        result_dict = {
            "ExitCode": 0, 
            "ErrorCode": "", 
            "ErrorMessage": "", 
            "Detail": ""
        }

        result = Result(result_dict)

        self.assertEqual(result.ExitCode, 0)
        self.assertEqual(result.ErrorMessage, "")
        self.assertEqual(result.ErrorCode, "")
        self.assertEqual(result.Detail, "")

        return result.detail()

    def get_instance(self):

        instance_dict = {
            "InstanceId": 123,
            "State": "",
            "StartTime": "", 
            "EndTime": "", 
            "RetryCount": 6, 
            "Progress": 50, 
            "StdoutRedirectPath": "", 
            "StderrRedirectPath": "", 
            "Result": self.get_result() 
        }

        instance = Instance(instance_dict)

        self.assertEqual(instance.InstanceId, 123)
        self.assertEqual(instance.State, "")
        self.assertEqual(instance.StartTime, "")
        self.assertEqual(instance.EndTime, "")
        self.assertEqual(instance.RetryCount, 6)
        self.assertEqual(instance.Progress, 50)
        self.assertEqual(instance.StdoutRedirectPath, "")
        self.assertEqual(instance.StderrRedirectPath, "")
        self.assertEqual(instance.Result.detail(), self.get_result()) 

        return instance.detail()

    def testGroup(self):
        self.get_group()

    def testMetrics(self):
        self.get_metrics()

    def testCluster(self):
        self.get_cluster()

    def testTaskMetrics(self):
        self.get_task_metrics()

    def testInstanceMetrics(self):
        self.get_instance_metrics()

    def testJob(self):
        self.get_job()

    def testDisk(self):
        self.get_disk()

    def testImage(self):
        self.get_image()

    def testResult(self):
        self.get_result()

    def testInstance(self):
        self.get_instance()

if __name__ == '__main__':
    unittest.main()
