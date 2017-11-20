# -*- coding: utf-8 -*-

from __future__ import division, print_function
import atexit
import colorlog
import drmaa
import os
import stat
import sys
from collections import defaultdict
from hashlib import md5
from jug import init as juginit, task as jugtask
from jug.subcommands import SubCommand
from math import ceil
from random import shuffle
from time import time, sleep
from .errors import UnsupportedDRMAAVersion, UnrecognizedQueueSystem, CleanExit
from .errors import UnsupportedFeature
from .queues import SystemSGE, SystemSLURM, SystemLSF
from .resources import SGE, GE, SLURM, LSF


if sys.version_info.major == 2:
    input = raw_input  # noqa

# TODO
# * SLURM's reference http://apps.man.poznan.pl/trac/slurm-drmaa#Nativespecification
# * LSF https://github.com/PlatformLSF/lsf-drmaa (a nice table on the README under "Native Specification")
# * SGE - man qsub (i.e. -pe smp 8 -c 10 ... )
# * Possibly replace drmaa with gc3pie

__all__ = [
    "ScheduleCommand",
]

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s"))

logger = colorlog.getLogger()
# Remove the stderr logger
try:
    logger.handlers.pop()
except IndexError:
    pass
logger.addHandler(handler)


class Job(object):
    SLOT = {
        "free": set((
            drmaa.JobState.DONE,
            drmaa.JobState.FAILED,
        )),
        "queue": set((
            drmaa.JobState.UNDETERMINED,
            drmaa.JobState.QUEUED_ACTIVE,
        )),
        "hold": set((
            drmaa.JobState.SYSTEM_ON_HOLD,
            drmaa.JobState.USER_ON_HOLD,
            drmaa.JobState.USER_SYSTEM_ON_HOLD,
        )),
        "suspend": set((
            drmaa.JobState.SYSTEM_SUSPENDED,
            drmaa.JobState.USER_SUSPENDED,
        )),
        "run": set((
            drmaa.JobState.RUNNING,
        )),
    }

    def __init__(self, session, jobid):
        self.jobid = jobid
        self.session = session

    def reap(self):
        """Collect job info if it has already finished.

        Returns None if info is not available (usually job still active)

        Calling this function is necessary to obtain job statistics from the
        DRMAA session. Collecting this info will also avoid a memory leak
        """
        try:
            info = self.session.wait(self.jobid, self.session.TIMEOUT_NO_WAIT)
        except drmaa.errors.DrmaaException:
            # Failed to obtain job information
            info = None

        return info

    def wait(self):
        return self.session.wait(self.jobid, self.session.TIMEOUT_WAIT_FOREVER)

    def kill(self):
        """Kills the specified job
        """
        try:
            self.session.control(self.jobid, drmaa.JobControlAction.TERMINATE)
        except (drmaa.errors.InternalException, drmaa.errors.InvalidJobException):
            # Job may have died already
            pass

    def _get_status(self, category):
        status = self.session.jobStatus(self.jobid)
        return status in self.SLOT[category]

    def is_done(self):
        return self._get_status("free")

    def is_queued(self):
        return self._get_status("queue")

    def is_held(self):
        return self._get_status("hold")

    def is_suspended(self):
        return self._get_status("suspend")

    def is_active(self):
        return self._get_status("active")


class SessionHandler(object):

    def __init__(self, options, store):
        # target: {job, job}
        self.assigned = defaultdict(set)
        # target: status: nr_of_jobs
        self.status = defaultdict(lambda: defaultdict(int))
        self.task_resources = {}

        self.used_jobs = 0
        self.store = store
        self.jugfile = options.jugfile
        self._jugfile_hash = self._compute_jughash()
        self.jugdir = options.jugdir
        self.max_jobs = options.schedule_max_jobs
        self.max_array = options.schedule_max_array
        self.script = options.schedule_script
        self.logs = options.schedule_logs
        self.stop_on_error = options.schedule_stop_on_error
        self.allow_jugfile_changes = options.schedule_allow_jugfile_changes

        self.s = drmaa.Session()
        self.s.initialize()
        atexit.register(lambda s: s.exit(), self.s)

        self.check_version()
        self._system = None
        self._identify_system()

    def _compute_jughash(self):
        mhash = md5()
        with open(self.jugfile, 'rb') as fh:
            for chunk in fh:
                mhash.update(chunk)

        return mhash.hexdigest()

    def _identify_system(self):
        if SLURM in self.s.drmsInfo:
            self._system = SystemSLURM()
        elif LSF in self.s.drmsInfo:
            self._system = SystemLSF()
        elif SGE in self.s.drmsInfo or GE in self.s.drmsInfo:
            self._system = SystemSGE()
        else:
            raise UnrecognizedQueueSystem(self.s.contact, self.s.drmsInfo,
                                          self.s.drmaaImplementation, self.s.version)

        logger.debug("Identified cluster system '%s'", self._system)

    def info(self):
        logger.info("Supported contact strings: %s", self.s.contact)
        logger.info("Supported DRM systems: %s", self.s.drmsInfo)
        logger.info("Supported DRMAA implementations: %s", self.s.drmaaImplementation)
        logger.info("Version %s", self.s.version)

    def check_version(self):
        if self.s.version.major != 1:
            raise UnsupportedDRMAAVersion(self.s.version)

    def is_complete(self):
        complete = True

        for target in self.status:
            ready = self.status[target]["ready"]
            wait = self.status[target]["wait"]
            active = self.status[target]["active"]
            if ready + wait + active > 0:
                complete = False
                break

        return complete

    def _add_job(self, target, jobid):
        # Create a job instance
        job = Job(self.s, jobid)

        self.assigned[target].add(job)
        self.used_jobs += 1

    def _rm_job(self, target, job):
        self.assigned[target].remove(job)
        self.used_jobs -= 1

    def launch_job(self, jobtemplate, bulk=0):
        try:
            if bulk > 1:
                return self.s.runBulkJobs(jobtemplate, beginIndex=1, endIndex=bulk, step=1)
            else:
                return self.s.runJob(jobtemplate)
        except drmaa.errors.DrmaaException:
            logger.exception("An error happened while submitting job(s) from "
                             "target %s to the queue", jobtemplate.jobName)
            raise CleanExit()

    def run(self, target, jobs=1, wait_cycles=8, wait_cycle_time=15):
        logger.info("Starting %s jobs on target %s", jobs, target)

        jt = self.s.createJobTemplate()
        jt.remoteCommand = self.script
        jt.args = ["execute",
                   "--target", target,
                   "--jugdir", self.jugdir,
                   "--nr-wait-cycles", str(wait_cycles),
                   "--wait-cycle-time", str(wait_cycle_time),
                   "--keep-failed",
                   self.jugfile,
                   ]

        # User arguments specified on the command-line
        # sys.argv = ["jugfile.py", args]
        if sys.argv[1:]:
            jt.args += ["--"] + sys.argv[1:]

        jt.jobName = target
        jt.jobEnvironment = os.environ.copy()
        jt.workingDirectory = os.getcwd()

        # Construct jt.nativeSpecification with specified resources
        res = self._system.native_resources(self.task_resources[target])
        logger.debug("Job will be submitted with the following resources '%s'", res)
        jt.nativeSpecification = res

        # NOTE: We need a colon as a prefix for output/errorPath. Weird DRMAA requirement
        if self._system.is_slurm():
            logger.debug("SLURM requires an explicit filename for output logs")
            # Currently only SLURM suffers from this
            # SGE and LSF can recognize a path and keep default filename
            # TODO Replace .format below with %x when SLURM 16.x support ends.
            jt.outputPath = ":" + os.path.join(self.logs,
                                               "jug-{}-%A_%a.out".format(jt.jobName))
            jt.errorPath = ":" + os.path.join(self.logs,
                                              "jug-{}-%A_%a.err".format(jt.jobName))
        else:
            # join an empty '' to ensure we get a trailing slash
            jt.outputPath = ":" + os.path.join(self.logs, '')
            jt.errorPath = jt.outputPath

        logger.debug("Running %s with %s and logs to %s", jt.remoteCommand, jt.args, jt.outputPath)

        if jobs == 1:
            jobid = self.launch_job(jt)
            self._add_job(target, jobid)
        else:
            if self._system.is_slurm():
                logger.warning(
                    "If you see a segmentation fault just after this warning, "
                    "check https://git.io/vQzY7 and contact your cluster administrator "
                    "to update libdrmaa.so to the latest available from: "
                    "https://github.com/ljyanesm/slurm-drmaa"
                )

            jobids = self.launch_job(jt, jobs)

            for jobid in jobids:
                self._add_job(target, jobid)

        self.s.deleteJobTemplate(jt)

        return jobid

    def collect_jobs(self):
        """Collect jobs that have ended and update existing slots accordingly
        """
        for target in self.assigned:
            for job in self.assigned[target].copy():
                if job.is_done():
                    jobinfo = job.reap()
                    logger.info("Reaped a jug instance from target %s - a queued job finished", target)

                    self._rm_job(target, job)

                    if jobinfo is None or jobinfo.exitStatus or jobinfo.wasAborted or jobinfo.hasSignal:
                        if jobinfo is not None:
                            logger.error("One jug instance terminated without returning any job information. "
                                         "This usually means the job was killed externally")
                        else:
                            logger.error("One jug instance failed with exit code %s , abort status %s "
                                         "and signal %s. Check %s for more information",
                                         jobinfo.exitStatus, jobinfo.wasAborted, jobinfo.terminatedSignal, self.logs)
                            logger.error("Additional job information: %s", jobinfo)

                        # If a job fails discard one slot
                        self.max_jobs -= 1

                        if self.stop_on_error:
                            raise CleanExit()
                    else:
                        logger.debug("One jug instance ended successfully. Additional job information: %s", jobinfo)

    def refresh_jug(self, retry=10):
        """Re-inits jug to ensure jug schedule is aware of all work left to be done
        This takes care of making tasks blocked by barriers or otherwise unreachable at start
        are made available
        """
        del jugtask.alltasks[:]
        try:
            self.store, jugspace = juginit(self.jugfile, self.jugdir, store=self.store)
        except (Exception, SystemExit) as e:
            logger.exception("Something went wrong while initializing the jugfile. Exception follows")
            if retry:
                logger.warning("Retrying for 5 minutes before giving up")
                sleep(30)
                self.refresh_jug(retry - 1)
            else:
                logger.warning("Ran out of retries. Giving up...")
                raise CleanExit()

    def update_status(self):
        """Computes the number of tasks in each status and how tasks are grouped
        as targets, taking into account their dependency graph
        """
        # Whenever we update the status of the project we also need to recompute
        # the targets because new tasks under new targets may now be available
        status = self.status
        status.clear()

        # And update what resources are to be allocated to each task set
        resources = self.task_resources
        resources.clear()

        # Make sure the jugfile didn't change since last check
        newhash = self._compute_jughash()
        if self._jugfile_hash != newhash:
            self._jugfile_hash = newhash
            if self.allow_jugfile_changes:
                logger.warn("Jugfile changes detected and 'allow_jugfile_changes' is set. Warranty void, use at your own risk")
            else:
                logger.error("jugfile changed during execution. This can have unexpected consequences and is not supported")
                raise UnsupportedFeature("jugfile changed during execution")

        # Reinitialize jug's task listing to ensure newly available tasks are picked up
        self.refresh_jug()

        for task in jugtask.alltasks:
            task_target = task.name
            try:
                resources[task_target] = task._resources
            except AttributeError:
                # Tasks not decorated with ResourcesTaskGenerator
                resources[task_target] = {}

            if task.is_locked():
                if task.is_failed():
                    status[task_target]["failed"] += 1
                else:
                    status[task_target]["active"] += 1
            elif task.can_load():
                status[task_target]["done"] += 1
            elif task.can_run():
                status[task_target]["ready"] += 1
            else:
                status[task_target]["wait"] += 1

        logger.debug("Internal status is %s", status)

    def assign_jobs(self):
        """Distribute available jobs between targets taking into account how
        many jobs were already assigned to a given target

        At most 50% of available jobs (rounded up) are distributed each iteration
        """
        # Display assigned jobs so far
        assigned_counts = ["    {}: {}".format(n, len(self.assigned[n]))
                           for n in sorted(self.assigned)]
        if assigned_counts:
            logger.info("Jobs submitted:\n" + '\n'.join(assigned_counts))

        total_pending = 0
        total_failing = 0
        # / 2 is used here to only allocate 50% of available resources every iteration
        available_jobs = int(ceil((self.max_jobs - self.used_jobs) / 2))

        if available_jobs == 0:
            logger.info("All job slots are in use (%s) or we are out of slots - No new jobs queued", self.used_jobs)
            return

        if available_jobs > self.max_array:
            logger.info("Got more jobs than maximum array size (%s > %s) - Limiting to this value", available_jobs, self.max_array)
            available_jobs = self.max_array

        allocation = {}

        for target in self.status:
            failed = self.status[target]["failed"]
            active = self.status[target]["active"]
            pending = self.status[target]["ready"]
            assigned = len(self.assigned[target])

            working = assigned - active
            # working can be negative if jug processes are active due to something
            # external to this scheduler such as another process.

            if working > 0:
                pending -= working

            if pending < 0:
                # Enough jobs have been assigned already, just wait for them to complete
                pending = 0

            total_failing += failed
            total_pending += pending
            allocation[target] = pending

        if total_failing:
            logger.info("%s tasks are in failed state and will not be retried. "
                        "Use 'jug cleanup --failed-only' to clear this and allow retrying", total_failing)

        if total_pending == 0:
            free_jobs = self.max_jobs - self.used_jobs
            logger.info("All work is taken or complete - No new jobs queued "
                        "- %s free jobs", free_jobs)
            return

        # Compute distribution of jobs
        assigned = 0

        # Use one of two allocation strategies
        # If we have enough available jobs for all pending work, assign an exact number
        # otherwise assign based on the fraction of work left to do on each task
        if available_jobs >= total_pending:
            logger.debug("Job slots in excess of available work - Using exact slot assignment")
            for target in allocation:
                allocation[target] = alloc = int(allocation[target])
                assigned += alloc
        else:
            logger.debug("Not enough job slots for all pending work - Distributing slots fairly")
            for target in allocation:
                allocation[target] = alloc = int(available_jobs * allocation[target] / total_pending)
                assigned += alloc

        # With small numbers of available_jobs we may end up with ties or other
        # situations where nothing would be distributed. In this case pick
        # a random target that still has some work to be consumed.
        # Ties will eventually resolve themselves
        remaining = available_jobs - assigned

        all_targets = list(allocation.keys())

        while remaining > 0:
            logger.debug("Got %s unassigned jobs, randomly distributing", remaining)
            shuffle(all_targets)

            # If we managed to assign something this iteration
            assigned = False

            for target in all_targets:
                previous = len(self.assigned[target])
                pending = self.status[target]["ready"]
                active = self.status[target]["active"]
                current = allocation[target]

                # If more tasks than necessary have been assigned before nothing happens here
                unassigned = (pending + active) - previous

                if unassigned - current > 0:
                    allocation[target] += 1
                    remaining -= 1
                    assigned = True

                    if remaining == 0:
                        break

            # We didn't assign anything which means all work is taken
            if not assigned:
                logger.debug("%s jobs without work. Leaving them for next iteration", remaining)
                break

        logger.debug("This iteration job allocation was: %s", allocation)

        # Finally start the jobs
        for target, jobs in allocation.items():
            if jobs > 0:
                self.run(target, jobs)

    def keep_going(self):
        """Returns True unless all work is done or all jobs failed
        """
        self.update_status()

        # All jobs died, or all work is complete.
        # Also only quit when all active jobs ended
        if (self.max_jobs < 1 or self.is_complete()) and self.used_jobs == 0:
            return False

        return True

    def manage_jobs(self):
        # update_status() was already executed by keep_going()
        self.collect_jobs()
        self.assign_jobs()

    def terminate(self, wait=False):
        for target in self.assigned:
            for job in self.assigned[target].copy():
                if wait:
                    job.wait()
                else:
                    job.kill()


def main(session, cycle_secs):
    start = time()

    while session.keep_going():
        session.manage_jobs()

        delta = time() - start

        # Try to update once every 'cycle_secs' seconds so if last iteration
        # took longer than 'cycle_secs' skip the sleeping entirely
        if delta > cycle_secs:
            delta = round(delta - cycle_secs, 1)
            logger.info("Last iteration took %s seconds longer than specified cycle time (%s seconds). "
                        "To maintain decent performance you may want to increase "
                        "'--cycle-time' or store jugdir on a faster filesystem",
                        delta, cycle_secs)
        else:
            delta = round(cycle_secs - delta, 1)
            logger.info("Sleeping for %s seconds", delta)
            sleep(delta)

        # Consider start before we re-runing session.keep_going() so we take
        # into account the time used to reload the jugfile and submit tasks
        start = time()


def flush_std_streams():
    sys.stderr.flush()
    sys.stdout.flush()


def ask_yesno_action(msg):
    # Flush streams before asking user input
    flush_std_streams()

    choices = {"y": True, "n": False}
    while True:
        try:
            choice = input("\n" + msg + " (y/n)? ").lower()
        except KeyboardInterrupt:
            continue

        if choice not in choices:
            sys.stderr.write("Choice not understood. Please retry\n")
            continue

        return choices[choice]


def abort(session):
    sys.stderr.write("Received Ctrl+C / SIGINT\n")

    if session.used_jobs:
        if ask_yesno_action("Kill all queued jobs"):
            # Kill all queued jobs
            session.terminate()
        else:
            sys.stderr.write("Jobs left in the queue\n")


class ScheduleCommand(SubCommand):
    """Schedules jobs on a DRMAA compatible queue
    """
    name = "schedule"

    def run(self, store, options, *args, **kwargs):
        # Create the folder where jug log_files will be written
        logs = options.schedule_logs

        if not os.path.isdir(logs):
            os.mkdir(logs)

        # Check if 'script' was given and is executable
        if options.schedule_script != "jug":
            options.schedule_script = os.path.abspath(options.schedule_script)

            if not os.path.isfile(options.schedule_script):
                logger.error("--script: '%s' doesn't exist", options.schedule_script)
                sys.exit(1)

            if not os.access(options.schedule_script, os.X_OK):
                logger.warn("--script: '%s' is not executable. Attempting to fix", options.schedule_script)

                try:
                    st = os.stat(options.schedule_script)
                    os.chmod(options.schedule_script, st.st_mode | stat.S_IEXEC)
                except (OSError, IOError):
                    logger.error("Couldn't make --script: '%s' executable. Manually run 'chmod +x %s'",
                                 options.schedule_script, options.schedule_script)
                    sys.exit(1)

        s = SessionHandler(options, store)
        s.info()

        try:
            main(s, options.schedule_cycle)
        except KeyboardInterrupt:
            abort(s)
        except UnsupportedFeature:
            sys.stderr.write("A fatal error was encountered.\n")
            sys.stderr.write("Scheduler will now abort and jobs will be killed\n")
            s.terminate()
        except CleanExit:
            sys.stderr.write("A critical error was encountered.\n")
            sys.stderr.write("Check above for additional information\n")
            sys.stderr.write("Scheduler will now abort\n")
            sys.stderr.write("Waiting for active jobs to finish\n")
            sys.stderr.write("Hit Ctrl+C to cancel active jobs and exit\n")
            try:
                s.terminate(wait=True)
            except KeyboardInterrupt:
                s.terminate()

    def parse(self, parser):
        defaults = self.parse_defaults()

        parser.add_argument("--script", action="store",
                            dest="schedule_script",
                            help=("Script to use instead of '{schedule_script}'. "
                                  "Use this if your cluster environment needs to "
                                  "be setup before execution""".format(**defaults)))
        parser.add_argument("--max-jobs", action="store", type=int,
                            dest="schedule_max_jobs", metavar="MAX_JOBS",
                            help=("Maximum number of jobs to queue "
                                  "(Default: {schedule_max_jobs})".format(**defaults)))
        parser.add_argument("--max-array", action="store", type=int,
                            dest="schedule_max_array", metavar="MAX_ARRAY",
                            help=("Maximum array size for every queue submission "
                                  "(Default: {schedule_max_array})".format(**defaults)))
        parser.add_argument("--logs", action="store", dest="schedule_logs",
                            metavar="LOGS",
                            help=("Location to store logs from the queueing system "
                                  "(Default: '{schedule_logs}')".format(**defaults)))
        parser.add_argument("--cycle-time", action="store", type=int,
                            dest="schedule_cycle", metavar="CYCLE_TIME",
                            help=("Number of seconds between each queue action "
                                  "(Default: {schedule_cycle})".format(**defaults)))
        parser.add_argument("--stop-on-error", action="store_const", const="True",
                            dest="schedule_stop_on_error",
                            help="If a job fails, stop and until all jobs end")
        parser.add_argument("--allow-jugfile-changes", action="store_const", const="True",
                            dest="schedule_allow_jugfile_changes",
                            help=("If jugfile changes, continue anyways and "
                                  "try to recover from parsing errors. "
                                  "This is an advanced option, so you should know what you are doing. "))

    def parse_defaults(self):
        return {
            "schedule_max_jobs": 20,
            "schedule_max_array": 1000,
            "schedule_logs": "jug_logs",
            "schedule_cycle": 60,
            "schedule_stop_on_error": False,
            "schedule_allow_jugfile_changes": False,
            "schedule_script": sys.argv[0] if sys.argv[0].startswith("/") else "jug",
        }


# vim: ai sts=4 et sw=4
