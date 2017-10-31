
import time
import arrow

from django.core.management.base import BaseCommand, CommandError
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.worker_helpers.worker_registry import get_worker


class Command(BaseCommand):
    help = 'Proccess local jobs.  This is mainly true for local jobs!, will only ask for things.'
    
    JobManager = get_manager('JobManager')
    
    
    def handle(self, *args, **options):
        
        try:
            self.run()
        except:
            raise
            print('A major failure has occured!')
    
    def run(self):
        start_time = arrow.utcnow()
        while start_time < arrow.utcnow().replace(minutes =+ 15): # run for a maximum of 15 minutes and then die!
            jobs = self.get_jobs()
            for job in jobs:
                
                manager = get_manager(job.model_name)
                
                models = manager.get_by_query(query_params = {'uuid' : job.model_uuid})
                
                if len(models) == 0: # we can no longer find that row, could happen if we delete, just skip over it.
                    continue
                else:
                    worker = models[0].get_worker()
                    worker.process_job_response(job_pk = job.pk, response = None, job_model = job) # since it is a local job, the worker will input some default values as the response

            if len(jobs)== 0: # if we're out of job, let program finish and cronjob restart it.
                break
            else:
                time.sleep(1)
            
            # we have not dealt with the fact we may have long running jobs.  This means that cronjob timer
            # will need to be set accordingly? we can always set to make sure the cronjob is the one there is a max of 1 of.
    
    def get_jobs(self):
        
        query = {
            "filter":{
                'job_type': 'local',  # get local jobs
                'status' : 1,         # get all that still need to be pending
                'run_at__lte':  arrow.utcnow().timestamp # get all that should be run now.
                } # 
            }
        jobs = self.JobManager.get_by_query(query_params = query) # Get all Pending Jobs
        
        
        return jobs[0:10] # we limit to 10 to prevent any long running jobs overlapping on subsequent runs!