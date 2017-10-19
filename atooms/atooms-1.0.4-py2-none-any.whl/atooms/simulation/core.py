# This file is part of atooms
# Copyright 2010-2017, Daniele Coslovich

"""
Base simulation class with callback logic.

`atooms` provides a generic simulation interface that abstracts out
most of the common parts of particle-based simulations.

`Simulation` uses callbacks to analyze and process simulation data on
the fly. The module `atooms.simulation.observers` provides basic
callbacks to write data to disk, e.g. trajejectory files, and to stop
the simulation when certain targets are reached, e.g. mean squared
displacement larger than a threshold.

The interval in steps at which callbacks are executed is controlled by
a `Scheduler` instance.

The actual simulation code is wrapped by a simulation "backend" that
exposes a minimal but coherent interface.
"""

import os
import time
import datetime
import logging

from atooms.core import __version__
from atooms.core.utils import mkdir, barrier
from .observers import target_steps, Speedometer, Scheduler, SimulationEnd

_log = logging.getLogger(__name__)


def _report(info, file_handle=None, log_echo=True):
    """
    Log `info` string to default logger at level info.

    Optionally write `info` to `file_handle` if the latter is
    given. Logging is disabled via `log_echo` is False.
    """
    if info is None:
        return

    if log_echo:
        for line in info.split('\n'):
            _log.info(line.strip())

    if file_handle is not None:
        file_handle.write(info)


class Simulation(object):

    """Simulation base class."""

    version = __version__

    def __init__(self, backend, output_path=None, steps=0,
                 checkpoint_interval=0, enable_speedometer=False,
                 restart=False):
        """
        Perform a simulation using the specified `backend` and optionally
        write output to `output_path`. This can be a file or directory path.

        Paths: to define output paths we rely on `output_path`, all
        other paths are defined based on it and on its base_path.
        """
        self.backend = backend
        self.output_path = output_path
        self.steps = steps
        self._restart = restart
        self.current_step = 0
        self.initial_step = 0
        # We expect subclasses to keep a ref to the trajectory object
        # self.trajectory used to store configurations
        self.trajectory = self.backend.trajectory

        # Make sure the dirname of output_path exists. For instance,
        # if output_path is data/trajectory.xyz, then data/ should
        # exist. This creates the data/ folder and its parents folders.
        if self.output_path is not None:
            mkdir(os.path.dirname(self.output_path))

        # Internal variables
        self._callback = []
        self._start_time = time.time()
        self._speedometer = None
        self._checkpoint_scheduler = Scheduler(checkpoint_interval)
        self._targeter_steps = target_steps
        self._cbk_params = {}  # hold scheduler and parameters of callbacks
        if enable_speedometer:
            self._speedometer = Speedometer()
            self.add(self._speedometer, Scheduler(None, calls=20,
                                                  target=self.steps))

    @property
    def system(self):
        # Note that setting system as a reference in the instance, like
        #   self.system = self.backend.system
        # is unsafe because this won't follow the backend's system when the
        # latter is reassigned as in
        #   self.backend.system = None
        # So we defined it as a property.
        return self.backend.system

    @system.setter
    def system(self, value):
        self.backend.system = value

    def __str__(self):
        return 'atooms simulation via %s' % self.backend

    @property
    def restart(self):
        """True is the simulation should be restarted. Read-only property."""
        return self._restart

    @property
    def base_path(self):
        return os.path.splitext(self.output_path)[0]

    def add(self, callback, scheduler, *args, **kwargs):
        """
        Add an observer `callback` to be called along with a `scheduler`.

        `scheduler` and `callback` must be callables accepting a
        Simulation instance as unique argument. `scheduler` must
        return the next step at which the observer has to be notified.

        An integer value is allowed for `scheduler`. In this case, a
        scheduler with fixed interval is generated internally and the
        observer is notified every `scheduler` steps.
        """
        # If the callback is already there we replace it
        # This allows to update targets / schedules on the way
        # TODO: this way we cannot the same observer with different schedules
        if callback in self._callback:
            self._callback.remove(callback)

        # Accept an integer interval
        if type(scheduler) is int:
            scheduler = Scheduler(scheduler)

        # Store scheduler, callback and its arguments
        # in a separate dict (NOT in the function object itself!)
        self._cbk_params[callback] = {'scheduler': scheduler,
                                      'args': args,
                                      'kwargs': kwargs}

        # Keep targeters last
        if 'target' not in callback.__name__.lower():
            self._callback.insert(0, callback)
        else:
            self._callback.append(callback)

    def remove(self, callback):
        """Remove the observer `callback`."""
        if callback in self._callback:
            self._callback.remove(callback)
            self._cbk_params.pop(callback)
        else:
            _log.debug('attempt to remove inexistent callback %s (dont worry)', callback)

    def _notify(self, observers):
        for observer in observers:
            _log.debug('notify %s at step %d', observer, self.current_step)
            args = self._cbk_params[observer]['args']
            kwargs = self._cbk_params[observer]['kwargs']
            observer(self, *args, **kwargs)

    @property
    def _targeters(self):
        return [o for o in self._callback if 'target' in o.__name__.lower()]

    @property
    def _non_targeters(self):
        return [o for o in self._callback if 'target' not in o.__name__.lower()]

    @property
    def _speedometers(self):
        return [o for o in self._callback if isinstance(o, Speedometer)]

    def write_checkpoint(self):
        """Write checkpoint to allow restarting a simulation."""
        if self.output_path is not None:
            with open(self.output_path + '.chk.step', 'w') as fh:
                fh.write('%d' % self.current_step)
        # Do not use try/except to avoid catching wrong exceptions
        if hasattr(self.backend, 'write_checkpoint'):
            self.backend.write_checkpoint()

    def read_checkpoint(self):
        """
        Read the checkpoint to restart a simulation.

        If the checkpoint file is not found, this method fails
        gracefully.
        """
        if self.output_path is not None:
            if os.path.exists(self.output_path + '.chk.step'):
                with open(self.output_path + '.chk.step') as fh:
                    self.current_step = int(fh.read())
            else:
                _log.debug('could not find checkpoint')

        # Do not use try/except to avoid catching wrong exceptions
        if hasattr(self.backend, 'read_checkpoint'):
            self.backend.read_checkpoint()

    @property
    def rmsd(self):
        try:
            return self.backend.rmsd
        except AttributeError:
            return 0.0

    def _elapsed_wall_time(self):
        """Elapsed wall time in seconds."""
        return time.time() - self._start_time

    def wall_time(self, per_step=False, per_particle=False):
        """
        Elapsed wall time in seconds.

        Optionally normalized per step and or per particle. It can be
        subclassed by more complex simulation classes.
        """
        norm = 1.0
        # Normalize per particle
        if per_particle:
            if len(self.system.particle) > 0:
                norm *= len(self.system.particle)
            else:
                return float('nan')
        # Normalize per step
        if per_step:
            if self.current_step - self.initial_step > 0:
                norm *= (self.current_step - self.initial_step)
            else:
                return float('nan')
        return self._elapsed_wall_time() / norm

    def run_until(self, steps):
        """
        Run the simulation up to `steps`.

        Subclasses must set steps.
        """
        self.backend.run(steps - self.current_step)
        self.current_step = steps

    def run(self, steps=None):
        """Run the simulation."""
        # If we are restaring we do not allow changing target steps on the fly.
        # because it might have side effects like non constant writing interval.
        if steps is not None:
            if not self.restart or self.current_step == 0:
                self.steps = steps

        # Targeter for steps. This will the replace an existing one.
        self.add(self._targeter_steps, Scheduler(self.steps),
                 self.current_step + self.steps)

        # Report
        _report(self._info_start())
        _report(self._info_backend())
        _report(self._info_observers())

        # Read checkpoint if we restart
        if self.restart:
            self.read_checkpoint()
        barrier()
        self.initial_step = self.current_step
        self._start_time = time.time()

        # Reinitialize speedometers
        for s in self._speedometers:
            s._init = False

        try:
            # Before entering the simulation, check if we can quit right away
            self._notify(self._targeters)
            # Then notify non targeters unless we are restarting
            if self.current_step == 0:
                self._notify(self._non_targeters)
            else:
                self._notify(self._speedometers)
            _log.info('starting at step: %d', self.current_step)
            while True:
                # Run simulation until any of the observers need to be called
                all_steps = [self._cbk_params[c]['scheduler'](self) for c in self._callback]
                next_checkpoint = self._checkpoint_scheduler(self)
                next_step = min(all_steps + [next_checkpoint])
                self.run_until(next_step)

                # Find observers indexes corresponding to minimum step
                # then get all corresponding observers
                next_step_ids = [i for i, step in enumerate(all_steps) if step == next_step]
                next_observers = [self._callback[i] for i in next_step_ids]

                # Observers should be sorted such that targeters are
                # last to avoid cropping output files
                self._notify(next_observers)
                if self.current_step == next_checkpoint:
                    self.write_checkpoint()

        except SimulationEnd:
            # Checkpoint configuration at last step
            self.write_checkpoint()
            _report(self._info_end())

        except KeyboardInterrupt:
            pass

        except:
            _log.error('simulation failed')
            raise

    def _info_start(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')
        txt = """\

        {}

        version: {}
        atooms version: {}
        simulation started on: {}
        output path: {}\
        """.format(self, self.version, __version__, now, self.output_path)
        return txt

    def _info_backend(self):
        """Subclasses may want to override this method."""
        txt = 'backend: {}\n'.format(self.backend)
        if hasattr(self.backend, 'version'):
            txt += 'backend version: %s\n' % self.backend.version
        return txt

    def _info_observers(self):
        txt = []
        for f in self._callback:
            params = self._cbk_params[f]
            s = params['scheduler']
            if 'target' in f.__name__.lower():
                args = params['args']
                txt.append('target %s: %s' % (f.__name__, args[0]))
            else:
                txt.append('writer %s: interval=%s calls=%s' %
                           (f.__name__, s.interval, s.calls))
        return '\n'.join(txt)

    def _info_end(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')
        txt = """
        simulation ended on: {}
        final steps: {}
        final rmsd: {:.2f}\
        wall time [s]: {:.1f}
        average TSP [s/step/particle]: {:.2e}\
        """.format(now, self.current_step, self.rmsd,
                   self.wall_time(), self.wall_time(per_step=True,
                                                    per_particle=True))
        return txt
