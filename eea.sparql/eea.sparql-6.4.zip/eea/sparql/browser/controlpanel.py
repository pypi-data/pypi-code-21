""" Control panel
"""
import inspect
import logging
import datetime
import pytz
import DateTime

from zope.component import queryUtility
from zope.interface import Interface, implementer
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from eea.sparql.content.sparql import async_updateLastWorkingResults
from eea.sparql.async import IAsyncService
logger = logging.getLogger("eea.sparql")


def sparql_check_sendmail(context):
    """ Check sparql and send email
    """
    status = ScheduleStatus(context, {})
    status(check_sendmail=True)

    async_service = queryUtility(IAsyncService)
    if async_service is not None:
        delay = datetime.timedelta(days=1)
        queue = async_service.getQueues()['']
        async_service.queueJobInQueueWithDelay(
            None, datetime.datetime.now(pytz.UTC) + delay,
            queue, ('sparql',),
            sparql_check_sendmail,
            context,
        )


class IScheduleStatus(Interface):
    """ Control Panel Schedule
    """
    def schedule_check(self):
        """ Schedule check to zc.async
        """


@implementer(IScheduleStatus)
class ScheduleStatus(BrowserView):
    """ Async Schedule Status of Sparql Queries
    """
    index = ViewPageTemplateFile("schedule_status.pt")

    def schedule_check(self):
        """ Schedule zc.async job to check and send email periodically
        """
        async_service = queryUtility(IAsyncService)
        if not async_service:
            return sparql_check_sendmail(self.context)

        queue = async_service.getQueues()['']
        async_service.queueJobInQueue(
            queue, ('sparql',),
            sparql_check_sendmail,
            self.context
        )
        return 'OK'

    def __call__(self, check_sendmail=False):
        start_spq_path = self.request.get('start_spq_path', None)
        if start_spq_path:
            self.restartSparql(start_spq_path)

        self.updUnqSparqls()

        if self.request.get('start_all_spq', None):
            self.startAllUnqSparqls()

        self.updUnqSparqlStatus()

        if check_sendmail:
            return self.checkAllUnqSparqls()

        return self.index()

    def getAsyncJobs(self):
        """Returns the jobs from the async queue which are either
        queued or active
        """
        async_service = queryUtility(IAsyncService)
        if async_service is None:
            return

        async_queue = async_service.getQueues()['']

        # queued jobs
        for job in async_queue:
            yield job

        # active jobs
        for disp in async_queue.dispatchers.values():
            for agent in disp.values():
                for job in agent:
                    yield job

    def getSparqlAsyncJobs(self):
        """Returns the sparql jobs from the async queue which are either
        queued or active
        """

        portal_path = self.context.getPhysicalPath()

        for job in self.getAsyncJobs():
            if not job.args:
                continue
            job_context = job.args[0]
            if isinstance(job_context, tuple) and \
                    job_context[:len(portal_path)] == portal_path:
                job_argnames = inspect.getargspec(job.callable).args
                for argn, argv in zip(job_argnames, job.args):
                    if argn != 'func':
                        continue
                    elif argv.func_name == 'async_updateLastWorkingResults':
                        yield job

    def updUnqSparqls(self):
        """Retrieves and stores details about sparql queries
        which have a repeatable refresh rate, and which are not
        in the async queue
        """

        # paths of queued sparqls
        q_sparql_paths = set()

        for job in self.getSparqlAsyncJobs():
            spq_path = '/'.join(job.args[0])
            if spq_path not in q_sparql_paths:
                q_sparql_paths.add(spq_path)

        # details of unqueued sparqls
        self.unq_sparqls = {}

        p_catalog = getToolByName(self.context, 'portal_catalog')
        spq_brains = p_catalog.searchResults(portal_type='Sparql')
        for brain in spq_brains:
            spq_path = brain.getPath()
            if spq_path not in q_sparql_paths:
                spq_ob = brain.getObject()
                if spq_ob.refresh_rate != 'Once':
                    self.unq_sparqls[spq_path] = {
                        'spq_title':brain.Title,
                        'spq_url':brain.getPath(),
                        'spq_rrate':spq_ob.refresh_rate
                        }

    def restartSparql(self, spq_path):
        """Refreshes a sparql query and schedules it in the async queue;
        the argument is the relative path of sparql object
        """
        async_service = queryUtility(IAsyncService)
        if async_service is None:
            logger.warn(
                "Can't restartSparql. plone.app.async NOT installed!")
            return

        p_catalog = getToolByName(self.context, 'portal_catalog')
        spq_brain = p_catalog.searchResults(
            portal_type='Sparql', path=spq_path)[0]
        spq_ob = spq_brain.getObject()

        if spq_ob and spq_ob.getRefresh_rate() != 'Once':
            spq_ob.scheduled_at = DateTime.DateTime()
            logger.info('[Restarting Sparql]: %s', spq_brain.getPath())
            try:
                async_queue = async_service.getQueues()['']
                async_service.queueJobInQueue(
                    async_queue, ('sparql',),
                    async_updateLastWorkingResults,
                                        spq_ob,
                                        scheduled_at=spq_ob.scheduled_at,
                                        bookmarks_folder_added=False)
            except Exception, e:
                logger.error("Got exception %s when restarting sparql %s",
                                      e, spq_brain.getPath())

    def updUnqSparqlStatus(self):
        """Updates the variable 'unq_sparql_status' which stores the view's
        main output
        """

        self.unq_sparql_status = []

        # paths of unqueued sparqls
        unq_sparql_paths = set(self.unq_sparqls.keys())

        for spq_path in unq_sparql_paths:
            self.unq_sparql_status.append({
                'path': spq_path,
                'title': self.unq_sparqls[spq_path]['spq_title'],
                'url': self.unq_sparqls[spq_path]['spq_url'],
                'rrate': self.unq_sparqls[spq_path]['spq_rrate']
                })

    def getUnqSparqlStatus(self):
        """Returns the view's main output; getter for
        'self.unq_sparql_status'
        """

        return self.unq_sparql_status

    def startAllUnqSparqls(self):
        """Refreshes all sparql queries which are not in the async queue and
        schedules them in the queue
        """

        # paths of unqueued sparqls
        unq_sparql_paths = set(self.unq_sparqls.keys())

        if not unq_sparql_paths:
            return None

        for spq_path in unq_sparql_paths:
            self.restartSparql(spq_path)

        self.updUnqSparqls()

    def checkAllUnqSparqls(self):
        """Checks for sparql queries not in the async queue. If found, sends a
        notification e-mail to the development team, and then schedules the
        stopped queries in the async queue
        """

        cnt_unq_sparqls = len(self.unq_sparql_status)

        if cnt_unq_sparqls == 0:
            return_msg = "No unqueued sparql queries found. E-mail not sent."
            return return_msg

        mailhost = getToolByName(self.context, "MailHost")

        email_from = "no-reply@eea.europa.eu"

        portal_props = getToolByName(self.context, 'portal_properties')
        site_props = getattr(portal_props, 'site_properties')
        email_to = getattr(site_props, 'development_team_email')

        subject = "[EEA Sparql Status] " + \
                  str(cnt_unq_sparqls) + " unqueued sparql queries"
        body = "Found " + str(cnt_unq_sparqls) + \
                    " sparql queries not scheduled in the async queue:\n"

        for row in self.unq_sparql_status:
            body += "\n* " + row['title'] + " <" + row['url'] + ">"
        body += "\n\nRestarting them ...\n\n" + \
            "Details about the current stopped queries can be found here: " + \
            "EEA Sparql Schedule Status <"  + \
            self.context.absolute_url() + "/@@sparql-schedule-controlpanel>\n"

        return_msg = "Found unqueued sparql queries. "

        try:
            logger.info('Sending e-mail to %s', email_to)
            mailhost.send(mfrom=email_from, mto=email_to,
                subject=subject, messageText=body)
        except Exception, e:
            logger.error("Got exception %s for %s", e, email_to)
            return_msg += "Error raised while attempting to send e-mail. "
        else:
            return_msg += "E-mail sent. "

        self.startAllUnqSparqls()

        return return_msg
