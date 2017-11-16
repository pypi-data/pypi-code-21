'''
Tios_receiver complements tios_transmitter.

A tios receiver is initialised with a tios job ID:

    tr = tios.receiver('abc123')

It collects a new frame of data every time the step() method is called:

    tr.step()

To see if the simulation is still running, use the is_running method:

    alive = tr.is_running()

NOTE: tr.step() does not return with an error if the simulation is stopped - it
just waits until it starts again.

The receiver has an MDTraj trajectory attribute with data for the current 
snapshot. This is updated each time the step() method is called.

The recent history of certain simula.tion metrics - e.g. temperature, 
potential energy, are available via the monitors dictionary attribute. Each 
key is associated with a list that grows as frames are read. The available 
keys are: 'Timepoint', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 'Eangle',
'Edihe', 'Eimpr', 'RMSD'.

    rmsd_history = tr.monitors['RMSD']

'''
from tios import communication

import mdtraj as mdt
import numpy as np
import time

class TiosReceiver(object):
    def __init__(self, id, protocol='Mongo', selection='all'):
        """
        Create a new receiver.

        Args:
            id (str): ID of the Tios job.
            protocol (str, optional): Communication protocol to use.
            selection (str, optional): selection string in MDTraj syntax for
                the subset of atoms to be included.

        Attributes:
            trajectory (MDTraj.Trajectory): Trajectory with current coordinates
            monitors (dict): Dictionary of simulation metrics (energies, etc.).
            timepoint (float): Age of the simulation, in picoseconds.

        """
        self._te = communication.TiosAgent(id, protocol=protocol)
        topology = self._te.topology
        self._box = self._te.box
        self._usersel = topology.select(selection)
        self._datasel = self._te.selection
        if set(self._usersel).issubset(set(self._datasel)):
            self._use_unsel = False
            self._sel = []
            for i in self._usersel:
                self._sel.append(self._datasel.index(i))
            self._xyz = self._te.xyzsel
        else:
            self._use_unsel = True
            self._unsel = []
            for i in range(topology.n_atoms):
                if not i in self._datasel:
                    self._unsel.append(i)
            self._xyz = np.zeros((topology.n_atoms, 3))
            self._xyz[self._datasel] = self._te.xyzsel
            self._xyz[self._unsel] = self._te.xyzunsel
            self._sel = self._usersel
        topology = topology.subset(self._usersel)
        self.trajectory = mdt.Trajectory(self._xyz[self._sel], topology)
        self.trajectory.unitcell_vectors=self._box
        self.monitors = self._te.monitors
        self.timepoint = self._te.timepoint
        self.trajectory.time = self.timepoint

    @property
    def status(self):
        """
        str: Current status of simulation.

        """
        return self._te.status

    def step(self, wait=True, killer=None):
        """
        Collect the next timestep of data from the simulation.

        Args:
            wait (bool, optional): If True, if the simulation is Stopped, wait
                for it to update. Otherwise return immediately.e
            killer (GracefulKiller, optional): hook to trap ctrl-C, etc.

        """
        newtimepoint = self.timepoint
        while newtimepoint == self.timepoint:
            if killer is not None:
                if killer.kill_now:
                    return
            if self.status != 'Running':
                if wait:
                    interval = 30
                else:
                    return
            else:
                if self._te.frame_rate == 0:
                    interval = 2.0
                else:
                    interval = max(2.0, 30.0 / self._te.frame_rate)
            time.sleep(interval)
            newtimepoint = self._te.timepoint
        self.timepoint = newtimepoint
        xyzsel = self._te.xyzsel
        if self._use_unsel:
            self._xyz[self._datasel] = xyzsel
            self._xyz[self._unsel] = self._te.xyzunsel
        else:
            self._xyz = xyzsel
        self.trajectory.xyz = self._xyz[self._sel]
        self.trajectory.time = self.timepoint
        self.monitors = self._te.monitors

    def is_running(self):
        """
        Return True if the simulation appears to be running.

        """
        return self.status == 'Running'
