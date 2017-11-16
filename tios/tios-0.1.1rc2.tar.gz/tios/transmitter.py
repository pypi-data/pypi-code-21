'''
Tios_transmitter: runs an MD code and streams the data using the tios
protocol.

A tios transmitter can be created from a command-line style string:

    tt = from_command('gmx mdrun -deffnm test')

or from an existing entry in the tios database:

    tt = from_entry('abc123')

The simulation is launched via the start method:

    tt.start()

Being under IMD control, it is advanced to the next sampling interval
using the step method:

    tt.step()

And stopped using the stop method:

    tt.stop()

To check the simulation is still running, use the is_running method:

    alive = tt.is_running()

Once started, the standard output and standard error from the job are
available:

    print tt.stdout
    print tt.stderr

An MDtraj Trajectory object with a single frame - the current coordinates - 
is available:

    topology = tt.trajectory.topology
    crds = tt.trajectory.xyz

Values of certain simulation metrics - e.g. temperature, potential energy, 
are available via the monitors dictionary attribute.  The available keys 
are: 'Timepoint', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 'Eangle', 
'Edihe', 'Eimpr'.

'''
from tios import utilities, communication, imd_sim

import socket
import os
import numpy as np
import time
from collections import deque
import mdtraj as mdt

def from_command(command, title='', selection='all', trate=1.0, 
                 deque_length=50, protocol='Mongo'):
    """
    Create a Tios transmitter from a command line string.

    Args:
        command (str): command-line like string.
        title (str, optional): Descriptive title for the job.
        selection (str, optional): Atom selection in MDTraj syntax. These 
           atoms are stored separately in the database from the rest, 
           potentially reducing data transfer to the receiver.
        trate (float, optional): The IMD sampling interval in picoseconds.
            Defaults to 1ps.
        deque_length (int, optional): Length of data timeseries to retain.
            Defaults to 50.
        protocol (str, optional): Communication protocol to use. Defaults to
            "Mongo".

    Returns:
        An instance of a `TiosTransmitter`
    """
    imd_job = imd_sim.from_command(command)
    id = utilities.id_generator()
    is_duplicate = True
    while is_duplicate:
        try:
            te = communication.TiosAgent(id, protocol=protocol, new=True)
            is_duplicate = False
        except ValueError:
            id = utilities.id_generator()
    te.title = title
    te.trate = trate
    te.message = {'header' : None}
    te.md_code = utilities.md_code_from_string(command)
    inputs = utilities.string_to_inputs_dict(command)
    te.filepack = utilities.inputs_dict_to_filepack(inputs)
    te.checkpoint = None
    topology = imd_job.trajectory.topology
    sel = topology.select(selection).tolist()
    te.topology = topology
    te.selection = sel
    unsel = [i for i in range(topology.n_atoms) if not i in sel]
    te.box = imd_job.trajectory.unitcell_vectors
    te.xyzsel = imd_job.trajectory.xyz[:,sel][0]
    te.xyzunsel = imd_job.trajectory.xyz[:,unsel][0]
    monitors = {}
    for key in ['Timepoint', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 
                'Eangle', 'Edihe', 'Eimpr', 'RMSD']:
        monitors[key] = None
    te.monitors = monitors
    te.sync()
    return TiosTransmitter(imd_job, te)

def from_entry(id, protocol='Mongo',
               targetdir='', preamble=None, extra_args=None, trate=None):
    """
    Create a Tios transmitter from an entry in the Tios database.

    Args:
        id (str): The Tios ID.
        protocol (str, optional): The connection protocol. Defaults to "Mongo".
        targetdir (str, optional): The directory into which files should be
            unpacked and from which the job will be launched. Defaults to the
            current directory.
        preamble (str, optional): Preamble required for the command line, e.g.
            "mpirun -n 16".
        extra_args (str, optional): Extra arguments to be appended to the
            command line, e.g. from Gromacs, "-maxh 23".
        trate (float, optional): IMD sampling interval. Defaults to whatever
            is defined in the database entry.

    Returns:
        An instance of a `TiosTransmitter`

    """
    te = communication.TiosAgent(id, protocol=protocol)
    if te.status == 'Running':
        raise RuntimeError('Tios job {} is already running'.format(id))
    inputs = utilities.filepack_to_inputs_dict(te.filepack, targetdir=targetdir)
    if preamble is not None:
        inputs[-1] = preamble.split()
    if trate is None:
       trate = te.trate
    else:
       te.trate = trate
    run_command = utilities.inputs_dict_to_string(inputs)
    if extra_args is not None:
        run_command = run_command + " " + extra_args
    imd_job = imd_sim.from_command(run_command, checkpoint=te.checkpoint, trate=trate)
    te.message = {'header' : None}
    te.sync()
    return TiosTransmitter(imd_job, te)
        
class TiosTransmitter(object):
    def __init__(self, imd_sim, tios_agent):
        """
        Transmitter for an MD simulation job, as created by Tios

        Args:
            imd_sim (IMDJob): An instance of an `IMDJob`.
            tios_agent (TiosAgent): An instance of a `TiosAgent`

        Attributes:
            id (str): Tios ID for the running job.
            status (str): Status of the running job.
            trajectory (MDTraj.Trajectory): Single frame MD trajectory.
            monitors (dict): Dictionary of energy components.
            stdout (str): Contents of STDOUT from the running job.
            stderr (str): Contents of STDERR from the running job.

        """
        self._imd_sim = imd_sim
        self._te = tios_agent
        self.id = self._te.id
        self.status = imd_sim.status
        self._selection = self._te.selection
        self._topology = self._te.topology
        self._unselection = [i for i in range(self._topology.n_atoms) 
                             if not i in self._selection]
        self.monitors = self._te.monitors
        self.trajectory = imd_sim.trajectory
        self._start = mdt.Trajectory(imd_sim.trajectory.xyz, 
                                     imd_sim.trajectory.topology)
        self._te.framerate = 0.0
        self._te.md_version = utilities.installed_version(self._te.md_code)
        self._te.host = socket.gethostname()
        try:
            self._te.username = os.getlogin()
        except OSError:
            self._te.username = '(unknown)'
        self._te.frame_rate = 0.0
        self._te.timepoint = imd_sim.timepoint
        self._te.status = imd_sim.status
        self._te.sync()

    def start(self):
        """
        Launch the simulation.

        """
        self._imd_sim.start()
        self.stdout = self._imd_sim.stdout
        self.stderr = self._imd_sim.stderr
        if self._imd_sim.status != 'Running':
            print(self.stdout)
            print(self.stderr)
            raise RuntimeError('Job failed prematurely')
        self._te.status = self._imd_sim.status
        self.status = self._imd_sim.status
        self._te.sync()
        self._last_step_time = time.time()

    def stop(self):
        """
        Stop the simulation.

        """
        self._imd_sim.stop()
        self._te.status = self._imd_sim.status
        self.status = self._imd_sim.status
        if self._imd_sim.new_checkpoint:
            cpt = self._imd_sim.get_checkpoint()
            self._te.checkpoint = cpt
        self._te.sync()
        
    def step(self):
        """
        Move the simulation along to the next IMD sample point.

        """
        message = self._te.message
        if message['header'] == 'STOP':
            self.stop()
        else:
            self._imd_sim.step()
            crds = self._imd_sim.trajectory.xyz[0]
            self._te.xyzsel = crds[self._selection]
            self._te.xyzunsel = crds[self._unselection]
            energies = self._imd_sim.energies
            energies['Timepoint'] = self._imd_sim.timepoint
            if 'tstep' in energies:
                del energies['tstep']
            for key in energies:
                self.monitors[key] = energies[key]
            self._te.monitors = self.monitors
            if self._imd_sim.new_checkpoint:
                cpt = self._imd_sim.get_checkpoint()
                self._te.checkpoint = cpt
            now = time.time()
            self._te.frame_rate = 60.0 / (now - self._last_step_time)
            self._last_step_time = now
            self._te.timepoint = self._imd_sim.timepoint
            self._te.status = self._imd_sim.status
            self.status = self._imd_sim.status
            self._te.sync()

    def is_running(self):
         """
         Return True if the simulation appears to be running.

         """
         return self._imd_sim.is_running()

