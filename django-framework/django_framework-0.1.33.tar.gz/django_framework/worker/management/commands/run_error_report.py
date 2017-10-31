
import time
import arrow

from django.core.management.base import BaseCommand, CommandError
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.worker_helpers.worker_registry import get_worker


class Command(BaseCommand):
    
    help = 'A basic check that will attempt to ping Admin if certain metrics are not met on the Jobs.  Too many failed jobs etc...'
    
    JobManager = get_manager('JobManager')
    
    
    def handle(self, *args, **options):
        try:
            self.run()
        except:
            print('A major failure has occured while running the Run Timeout!')
    
    def run(self):
        raise NotImplemented('woot we havent written you yet.')
        
    def get_jobs(self):
        
#         run_at__lte':  arrow.utcnow().timestamp
        # you might have some queued up job?....
        jobs = self.JobManager.get_by_query(query_params = {"filter":{"status__gt" : 0, 'timeout_at__lte':arrow.utcnow().replace(hours =-1).timestamp }}) # Get all Pending Jobs
        return jobs