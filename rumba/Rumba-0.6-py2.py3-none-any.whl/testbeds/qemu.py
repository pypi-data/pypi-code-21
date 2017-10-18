#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import multiprocessing
import time
import subprocess
import os
import sys

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve

import rumba.model as mod
import rumba.log as log
import rumba.ssh_support as ssh_support

logger = log.get_logger(__name__)


class Testbed(mod.Testbed):
    def __init__(self, exp_name, bzimage_path=None, initramfs_path=None,
                 proj_name="ARCFIRE", password="root", username="root",
                 use_vhost=True):
        mod.Testbed.__init__(self, exp_name, username, password, proj_name)
        self.vms = {}
        self.shims = []
        self.vhost = use_vhost
        self.boot_processes = []
        self.bzimage_path = bzimage_path
        self.initramfs_path = initramfs_path

    # Prepend sudo to all commands if the user is not 'root'
    def may_sudo(self, cmds):
        if os.geteuid() != 0:
            for i in range(len(cmds)):
                cmds[i] = "sudo %s" % cmds[i]

    @staticmethod
    def _run_command_chain(commands, results_queue,
                           error_queue, ignore_errors=False):
        """
        Runs (sequentially) the command list.

        On error, breaks and dumps it in error_queue, and interrupts
        as soon as it is non-empty (unless ignore errors is True).

        :type commands: list
        :type results_queue: Queue
        :type error_queue: Queue
        :param commands: list of commands to execute
        :param results_queue: Queue of results of parallel processes
        :param error_queue: Queue of error(s) encountered
        :return: None
        """
        errors = 0
        for command in commands:
            if not error_queue.empty() and not ignore_errors:
                break
            logger.debug('executing >> %s', command)
            try:
                subprocess.check_call(command.split())
            except (subprocess.CalledProcessError, IOError) as e:
                error_queue.put(str(e))
                errors += 1
                if not ignore_errors:
                    break
            except KeyboardInterrupt as e:
                error_queue.put('Interrupted')
        if errors == 0:
            results_queue.put("Command chain ran correctly")
        else:
            results_queue.put("Command chain ran with %d errors" % errors)

    def recover_if_names(self, experiment):
        for node in experiment.nodes:
            for ipcp in node.ipcps:
                if isinstance(ipcp, mod.ShimEthIPCP):
                    shim_name, node_name = ipcp.name.split('.')
                    port_set = [x for x in self.vms[node_name]['ports']
                                if x['shim'].name == shim_name]
                    port = port_set[0]
                    port_id = port['port_id']
                    vm_id = self.vms[node_name]['id']
                    mac = '00:0a:0a:0a:%02x:%02x' % (vm_id, port_id)
                    logger.info('Recovering ifname for port: %s.',
                                port['tap_id'])
                    output = ssh_support.execute_command(
                        self,
                        node.ssh_config,
                        'mac2ifname ' + mac)
                    ipcp.ifname = output
                    ssh_support.execute_command(
                        self, node.ssh_config,
                        "ip link set dev %(ifname)s up"
                        % {'ifname': ipcp.ifname})

    def swap_in(self, experiment):
        """
        :type experiment mod.Experiment
        :param experiment: The experiment running
        """
        if os.geteuid() != 0:
            try:
                subprocess.check_call(["sudo", "-v"])
                if self.vhost and \
                        (not os.access("/dev/vhost-net", os.R_OK)
                         or not os.access("/dev/vhost-net", os.W_OK)
                         or not os.access("/dev/kvm", os.R_OK)
                         or not os.access("/dev/kvm", os.W_OK)):
                    raise Exception('Cannot open vhost device. Make sure it is '
                                    'available and you have rw permissions '
                                    'on /dev/vhost-net')
            except subprocess.CalledProcessError:
                raise Exception('Not authenticated')

        logger.info("swapping in")

        # Download the proper buildroot images, if the user did not specify
        # local images
        url_prefix = "https://bitbucket.org/vmaffione/rina-images/downloads/"
        if not self.bzimage_path:
            bzimage = '%s.prod.bzImage' % (experiment.prototype_name())
            self.bzimage_path = os.path.join(mod.cache_dir, bzimage)
            if not os.path.exists(self.bzimage_path):
                logger.info("Downloading %s" % (url_prefix + bzimage))
                urlretrieve(url_prefix + bzimage,
                            filename=self.bzimage_path)
                print("\n")
        if not self.initramfs_path:
            initramfs = '%s.prod.rootfs.cpio' % (experiment.prototype_name())
            self.initramfs_path = os.path.join(mod.cache_dir, initramfs)
            if not os.path.exists(self.initramfs_path):
                logger.info("Downloading %s" % (url_prefix + initramfs))
                urlretrieve(url_prefix + initramfs,
                            filename=self.initramfs_path)
                print("\n")

        logger.info('Setting up interfaces.')

        # Building bridges and taps
        shim_processes = []
        r_queue = multiprocessing.Queue()
        e_queue = multiprocessing.Queue()
        for shim in experiment.dif_ordering:
            if not isinstance(shim, mod.ShimEthDIF):
                # Nothing to do here
                continue
            self.shims.append(shim)
            ipcps = shim.ipcps
            command_list = []
            command_list += ('brctl addbr %(br)s\n'
                             'ip link set dev %(br)s up'
                             % {'br': shim.name}
                             ).split('\n')
            for node in shim.members:  # type:mod.Node
                name = node.name
                vm = self.vms.setdefault(name, {'vm': node, 'ports': []})
                port_id = len(vm['ports']) + 1
                tap_id = '%s.%02x' % (name, port_id)

                command_list += ('ip tuntap add mode tap name %(tap)s\n'
                                 'ip link set dev %(tap)s up\n'
                                 'brctl addif %(br)s %(tap)s'
                                 % {'tap': tap_id, 'br': shim.name}
                                 ).split('\n')
                if shim.link_speed > 0:
                    speed = '%dmbit' % shim.link_speed

                    # Rate limit the traffic transmitted on the TAP interface
                    command_list += (
                        'tc qdisc add dev %(tap)s handle 1: root '
                        'htb default 11\n'
                        'tc class add dev %(tap)s parent 1: classid '
                        '1:1 htb rate 10gbit\n'
                        'tc class add dev %(tap)s parent 1:1 classid '
                        '1:11 htb rate %(speed)s'
                        % {'tap': tap_id, 'speed': speed}
                    ).split('\n')

                vm['ports'].append({'tap_id': tap_id,
                                    'shim': shim,
                                    'port_id': port_id})
                ipcp_set = [x for x in ipcps if x in node.ipcps]
                if len(ipcp_set) > 1:
                    raise Exception("Error: more than one ipcp in common "
                                    "between shim dif %s and node %s"
                                    % (shim.name, node.name))
                ipcp = ipcp_set[0]  # type: mod.ShimEthIPCP
                assert ipcp.name == '%s.%s' % (shim.name, node.name), \
                    'Incorrect Shim Ipcp found: expected %s.%s, found %s' \
                    % (shim.name, node.name, ipcp.name)
                ipcp.ifname = tap_id
                # TODO deal with Ip address (shim UDP DIF).

            # Avoid stacking processes if one failed before.
            if not e_queue.empty():
                break
            # Launch commands asynchronously
            self.may_sudo(command_list)
            process = multiprocessing.Process(target=self._run_command_chain,
                                              args=(command_list,
                                                    r_queue,
                                                    e_queue))
            shim_processes.append(process)
            process.start()

        # Wait for all processes to be over.
        total_processes = len(shim_processes)
        max_waiting_time = 4 * total_processes
        over_processes = 0

        while over_processes < total_processes and max_waiting_time > 0:
            # Check for deadlock

            # Check for errors
            if not e_queue.empty():
                error_str = str(e_queue.get())
                logger.error('Testbed instantiation failed: %s', error_str)

                # Wait for the running processes to quit before swapping out
                for process in shim_processes:
                    process.join()

                raise Exception('Failure: %s' % error_str)
            try:
                # Check for results
                result = r_queue.get(timeout=1)
                if result == "Command chain ran correctly":
                    over_processes += 1
                    logger.debug('%s/%s processes completed',
                                 over_processes, total_processes)
            except:
                max_waiting_time -= 1

        if max_waiting_time == 0:
            logger.error("Swap in is in deadlock, aborting.")
            for process in shim_processes:
                process.terminate()
                time.sleep(0.1)
                process.join()
            raise Exception('Swap in is in deadlock')

        for process in shim_processes:
            process.join()

        logger.info('Interfaces setup complete. '
                    'Building VMs (this might take a while).')

        # Building vms

        boot_batch_size = max(1, multiprocessing.cpu_count() // 2)
        booting_budget = boot_batch_size
        boot_backoff = 12  # in seconds
        base_port = 2222
        vm_memory = 164  # in megabytes
        vm_frontend = 'virtio-net-pci'

        vmid = 1

        for node in experiment.nodes:
            name = node.name
            vm = self.vms.setdefault(name, {'vm': node, 'ports': []})
            vm['id'] = vmid
            fwdp = base_port + vmid
            fwdc = fwdp + 10000
            mac = '00:0a:0a:0a:%02x:%02x' % (vmid, 99)
            vm['ssh'] = fwdp
            vm['id'] = vmid
            node.ssh_config.hostname = "localhost"
            node.ssh_config.port = fwdp
            node.ssh_config.username = self.username
            node.ssh_config.password = self.password
            log_file = os.path.join(mod.tmp_dir, name + '.log')

            vars_dict = {'fwdp': fwdp, 'id': vmid, 'mac': mac,
                         'bzimage': self.bzimage_path,
                         'initramfs': self.initramfs_path,
                         'fwdc': fwdc,
                         'memory': vm_memory, 'frontend': vm_frontend,
                         'vmname': name,
                         'log_file' : log_file}

            host_fwd_str = 'hostfwd=tcp::%(fwdp)s-:22' % vars_dict
            vars_dict['hostfwdstr'] = host_fwd_str

            command = 'qemu-system-x86_64 '
            # TODO manage non default images
            command += ('-kernel %(bzimage)s '
                        '-append "console=ttyS0" '
                        '-initrd %(initramfs)s '
                        % vars_dict)
            if os.path.exists('/dev/kvm'):
                command += '--enable-kvm '
            command += ('-vga std '
                        '-display none '
                        '-smp 1 '
                        '-m %(memory)sM '
                        '-device %(frontend)s,mac=%(mac)s,netdev=mgmt '
                        '-netdev user,id=mgmt,%(hostfwdstr)s '
                        '-serial file:%(log_file)s '
                        % vars_dict
                        )

            del vars_dict

            for port in vm['ports']:
                tap_id = port['tap_id']
                mac = '00:0a:0a:0a:%02x:%02x' % (vmid, port['port_id'])
                port['mac'] = mac

                command += (
                    '-device %(frontend)s,mac=%(mac)s,netdev=data%(idx)s '
                    '-netdev tap,ifname=%(tap)s,id=data%(idx)s,script=no,'
                    'downscript=no%(vhost)s '
                    % {'mac': mac, 'tap': tap_id, 'idx': port['port_id'],
                       'frontend': vm_frontend,
                       'vhost': ',vhost=on' if self.vhost else ''}
                )

            booting_budget -= 1
            if booting_budget <= 0:
                logger.debug('Sleeping %s secs waiting '
                             'for the VMs to boot', boot_backoff)

                time.sleep(boot_backoff)
                booting_budget = boot_batch_size

            with open('%s/qemu_out_%s' % (mod.tmp_dir, vmid), 'w')\
                    as out_file:
                logger.debug('executing >> %s', command)
                self.boot_processes.append(subprocess.Popen(command.split(),
                                                            stdout=out_file))

            vmid += 1

        # Wait for the last batch of VMs to start
        if booting_budget < boot_backoff:
            tsleep = boot_backoff * (boot_batch_size - booting_budget) / \
                                            boot_batch_size
            logger.info('Sleeping %s secs '
                        'waiting for the last VMs to boot',
                        tsleep)
            time.sleep(tsleep)

        # TODO: to be removed, we should loop in the ssh part
        logger.info('Sleeping 5 seconds, just to be on the safe side')
        time.sleep(5)

        self.recover_if_names(experiment)

        logger.info('Experiment has been successfully swapped in.')

    def swap_out(self, experiment):
        """
        :rtype str
        :return: The script to tear down the experiment
        """
        logger.info('Killing qemu processes.')
        # TERM qemu processes
        for process in self.boot_processes:
            process.terminate()

        # Wait for them to shut down
        for process in self.boot_processes:
            process.wait()

        logger.info('Destroying interfaces.')
        port_processes = []
        error_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()
        for vm_name, vm in self.vms.items():
            for port in vm['ports']:
                tap = port['tap_id']
                shim = port['shim']

                commands = []
                commands += ('brctl delif %(br)s %(tap)s\n'
                             'ip link set dev %(tap)s down\n'
                             'ip tuntap del mode tap name %(tap)s'
                             % {'tap': tap, 'br': shim.name}
                             ).split('\n')
                self.may_sudo(commands)
                process = multiprocessing.Process(
                    target=self._run_command_chain,
                    args=(commands, results_queue, error_queue),
                    kwargs={'ignore_errors': True})
                port_processes.append(process)
                process.start()

        total_processes = len(port_processes)
        max_waiting_time = 2 * total_processes
        over_processes = 0

        while max_waiting_time > 0 and over_processes < total_processes:
            # Check for errors
            if not error_queue.empty():
                logger.warning('Failure while shutting down: %s',
                               str(error_queue.get()))
                over_processes += 1
            try:
                # Check for results
                result = results_queue.get(timeout=1)
                if result == "Command chain ran correctly":
                    over_processes += 1
                    logger.debug('%s/%s tear-down port '
                                 'processes completed',
                                 over_processes, total_processes)
            except:
                max_waiting_time -= 1

        error_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()
        shim_processes = []

        for shim in self.shims:
            commands = []
            commands += ('ip link set dev %(br)s down\n'
                         'brctl delbr %(br)s'
                         % {'br': shim.name}
                         ).split('\n')
            self.may_sudo(commands)
            process = multiprocessing.Process(target=self._run_command_chain,
                                              args=(commands,
                                                    results_queue,
                                                    error_queue),
                                              kwargs={'ignore_errors': True})
            shim_processes.append(process)
            process.start()

        total_processes = len(shim_processes)
        max_waiting_time = 2 * total_processes
        over_processes = 0

        while max_waiting_time > 0 and over_processes < total_processes:
            # Check for errors
            if not error_queue.empty():
                logger.warning('Failure while shutting down: %s'
                               % str(error_queue.get()))
                over_processes += 1
            try:
                # Check for results
                result = results_queue.get(timeout=1)
                if result == "Command chain ran correctly":
                    over_processes += 1
                    logger.debug('%s/%s tear-down shim '
                                 'processes completed'
                                 % (over_processes, total_processes))
            except:
                max_waiting_time -= 1
        logger.info('Experiment has been swapped out.')
