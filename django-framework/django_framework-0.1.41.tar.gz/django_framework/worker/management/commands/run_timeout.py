
import time
import arrow

from django.core.management.base import BaseCommand, CommandError
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.worker_helpers.worker_registry import get_worker


class Command(BaseCommand):
    
    help = 'Checks to see which jobs are now timed out.  This can be due to failed scripts etc.'
    
    JobManager = get_manager('JobManager')
    
    
    def handle(self, *args, **options):
        
        try:
            self.run()
        except:
            print('A major failure has occured while running the Run Timeout!')
    
    def run(self):
        
        jobs = self.get_jobs()
        jobs.update(**dict(status= -2, error_notes = 'no response within expected timeframe'))
        
        
            # we have not dealt with the fact we may have long running jobs.  This means that cronjob timer
            # will need to be set accordingly? we can always set to make sure the cronjob is the one there is a max of 1 of.
    
    def get_jobs(self):
        
#         run_at__lte':  arrow.utcnow().timestamp
        # you might have some queued up job?....
        jobs = self.JobManager.get_by_query(query_params = {"filter":{"status__gte" : 1, 'timeout_at__lte':arrow.utcnow().replace(hours =-1).timestamp }}) # Get all Pending Jobs
        return jobs