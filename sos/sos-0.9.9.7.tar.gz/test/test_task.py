#!/usr/bin/env python3
#
# This file is part of Script of Scripts (SoS), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/vatlab/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import os
import time
import unittest
import shutil
import glob

from sos.sos_script import SoS_Script, ParsingError
from sos.utils import env
from sos.sos_executor import Base_Executor
from sos.target import FileTarget
from sos.hosts import Host
import subprocess

class TestTask(unittest.TestCase):
    def setUp(self):
        env.reset()
        subprocess.call('sos remove -s', shell=True)
        #self.resetDir('~/.sos')
        self.temp_files = []
        Host.reset()

    def tearDown(self):
        for f in self.temp_files:
            FileTarget(f).remove('both')

    def touch(self, files):
        '''create temporary files'''
        if isinstance(files, str):
            files = [files]
        #
        for f in files:
            with open(f, 'w') as tmp:
                tmp.write('test')
        #
        self.temp_files.extend(files)

    def testWorkdir(self):
        '''Test workdir option for runtime environment'''
        import tempfile
        tdir = tempfile.mkdtemp()
        with open(os.path.join(tdir, 'aaa.pp'), 'w') as aaa:
            aaa.write('something')
        script = r"""
[0]
task: workdir={0!r}

with open(os.path.join({1!r}, 'result.txt'), 'w') as res:
   for file in os.listdir({1!r}):
       res.write(file + '\n')
""".format(os.path.split(tdir)[0], os.path.split(tdir)[1])
        wf = SoS_Script(script).workflow()
        env.config['sig_mode'] = 'force'
        env.config['wait_for_task'] = True
        Base_Executor(wf).run()
        with open(os.path.join(tdir, 'result.txt')) as res:
            content = [x.strip() for x in res.readlines()]
            self.assertTrue('aaa.pp' in content)

    def testSequential(self):
        '''Test concurrency option for runtime environment'''
        env.max_jobs = 5
        env.config['sig_mode'] = 'force'
        env.config['wait_for_task'] = True
        script =  SoS_Script(r"""
import time
[0]

repeat = range(4)
input: for_each='repeat'

task: concurrent=False

print('I am {}, waited {} seconds'.format(_index, _repeat + 1))
time.sleep(_repeat + 1)
print('I am {}, done'.format(_index))
""")
        env.config['wait_for_task'] = True
        wf = script.workflow()
        start = time.time()
        Base_Executor(wf).run()
        self.assertGreater(time.time() - start, 11)

    def testConcurrency(self):
        '''Test concurrency option for runtime environment'''
        env.max_jobs = 5
        env.config['sig_mode'] = 'force'#
        script =  SoS_Script(r"""
[0]

repeat = range(4)
input: for_each='repeat'

task: concurrent=True

import time
print('I am {}, waited {} seconds'.format(_index, _repeat + 1))
time.sleep(_repeat + 1)
print('I am {}, done'.format(_index))
""")
        wf = script.workflow()
        Base_Executor(wf).run()

    def testPrependPath(self):
        '''Test prepend path'''
        import stat
        if not os.path.isdir('temp'):
            os.mkdir('temp')
        with open('temp/temp_cmd', 'w') as tc:
            tc.write('echo "a"')
        os.chmod('temp/temp_cmd', stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)
        #
        script = SoS_Script(r"""
[1]
task:
run:
    temp_cmd
""")
        wf = script.workflow()
        env.config['sig_mode'] = 'force'
        #self.assertRaises(Exception, Base_Executor(wf).run)
        #
        # the following is supposed to create its own task file but
        # for some reason it uses the same task file
        #
        # use option env
        script = SoS_Script(r"""
[1]
task: env={'PATH': 'temp' + os.pathsep + os.environ['PATH']}
run:
    temp_cmd
""")
        wf = script.workflow()
        env.config['sig_mode'] = 'force'
        Base_Executor(wf).run()
        #
        #
        script = SoS_Script(r"""
[1]
task: prepend_path='temp'
run:
    temp_cmd
""")
        wf = script.workflow()
        Base_Executor(wf).run()


    def testActiveActionOption(self):
        '''Test the active option of actions'''
        # disallow
        self.assertRaises(ParsingError, SoS_Script, '''
[1]
rep = range(5)
input: for_each = 'rep'
# ff should change and be usable inside run
ff = "${_rep}.txt"
run:  active=1,2
echo ${ff}
touch temp/${ff}
''')
        #
        for active, result in [
            ('0', ['temp/0.txt']),
            ('-1', ['temp/4.txt']),
            ('(1,2)', ['temp/1.txt', 'temp/2.txt']),
            ('[2,3]', ['temp/2.txt', 'temp/3.txt']),
            ('(0,2,4)', ['temp/0.txt', 'temp/2.txt', 'temp/4.txt']),
            ('slice(1,None)', ['temp/1.txt', 'temp/2.txt', 'temp/3.txt', 'temp/4.txt']),
            ('slice(1,-2)', ['temp/1.txt', 'temp/2.txt']),
            ('slice(None,None,2)', ['temp/0.txt', 'temp/2.txt', 'temp/4.txt']),
            ]:
            if os.path.isdir('temp'):
                shutil.rmtree('temp')
            os.mkdir('temp')
            # test first iteration
            script = SoS_Script(('''
[1]
rep = range(5)
input: for_each = 'rep'
# ff should change and be usable inside run
ff = "${_rep}.txt"
run:  active=%s
echo ${ff}
touch temp/${ff}
''' % active).replace('/', os.sep))
            wf = script.workflow()
            env.config['sig_mode'] = 'force'
            env.config['wait_for_task'] = True
            Host.reset()
            Base_Executor(wf).run()
            files = list(glob.glob(os.path.join('temp', '*.txt')))
            self.assertEqual(sorted(files), sorted([x.replace('/', os.sep) for x in result]))
            #
            # test last iteration
            shutil.rmtree('temp')
            #
            # test active option for task
            os.mkdir('temp')
            script = SoS_Script(('''
[1]
rep = range(5)
input: for_each = 'rep'
# ff should change and be usable inside run
ff = "${_rep}.txt"
task:  active=%s
run:
echo ${ff}
touch temp/${ff}
''' % active).replace('/', os.sep))
            wf = script.workflow()
            env.config['sig_mode'] = 'force'
            env.config['wait_for_task'] = True
            Host.reset()
            Base_Executor(wf).run()
            files = list(glob.glob(os.path.join('temp', '*.txt')))
            self.assertEqual(sorted(files), sorted([x.replace('/', os.sep) for x in result]),
                    'With option {}'.format(active))
            #
            # test last iteration
            shutil.rmtree('temp')


    def testPassingVarToTask(self):
        '''Test passing used variable to tasks'''
        for i in range(10, 13):
            FileTarget('myfile_{}.txt'.format(i)).remove('both')
        #
        env.config['sig_mode'] = 'force'
        script = SoS_Script(r'''
parameter: gvar = 10

[10]
# generate a file
tt = range(gvar, gvar + 3)
input: for_each='tt'
output: "myfile_${_tt}.txt"
# additional comment

# _tt should be used in task
task: concurrent=True
run:
    echo ${_tt}_${_index} > ${_output!q}

''')
        wf = script.workflow()
        env.max_jobs = 4
        env.config['wait_for_task'] = True
        Base_Executor(wf).run()
        for t in range(10, 13):
            with open('myfile_{}.txt'.format(t)) as tmp:
                self.assertEqual(tmp.read(), str(t) + '_' + str(t-10) + '\n')
            FileTarget('myfile_{}.txt'.format(t)).remove('both')

    def testMaxJobs(self):
        '''Test default max number of jobs'''
        script = SoS_Script(r'''

[10]
input: for_each=[{'a': range(2)}, {'b': range(3)}]

task:
run:
    echo "a = ${a}, b = ${b}"
''')
        env.config['wait_for_task'] = True
        env.config['max_running_jobs'] = 2
        wf = script.workflow()
        Base_Executor(wf).run()

    @unittest.skipIf('TRAVIS_OS_NAME' in os.environ, 'Test fails on travis for unknown reason #831')
    def testKillAndPurge(self):
        '''Test no wait'''
        subprocess.call(['sos', 'purge'])
        script = SoS_Script(r'''
[10]
input: for_each=[{'a': range(2)}]

task:
run:
    echo Try to kill "a = ${a}"
    sleep 20
''')
        wf = script.workflow()
        env.config['sig_mode'] = 'force'
        env.config['max_running_jobs'] = 4
        env.config['wait_for_task'] = False
        ret = Base_Executor(wf).run()
        # sos should quit
        self.assertGreater(len(ret['pending_tasks']), 1)
        # wait for the task to start
        time.sleep(3)
        print('Running sos kill {}'.format(ret['pending_tasks'][0]))
        subprocess.call(['sos', 'kill', ret['pending_tasks'][0]])
        for i in range(20):
            output = subprocess.check_output(['sos', 'status', ret['pending_tasks'][0], '-v', '1']).decode()
            if 'killed' in output or 'aborted' in output or 'completed' in output:
                break
            self.assertFalse(i > 10, 'Task should be killed within 10 seconds, got {}'.format(output))
            time.sleep(1)
        #
        subprocess.call(['sos', 'kill', '--all'])
        for i in range(20):
            output = subprocess.check_output(['sos', 'status', ret['pending_tasks'][1], '-v', '1']).decode()
            if 'killed' in output or 'aborted' in output or 'completed' in output:
                break
            self.assertFalse(i > 10, 'Task should be killed within 10 seconds, got {}'.format(output))
            time.sleep(1)
        # test purge task
        subprocess.call(['sos', 'purge', ret['pending_tasks'][0]])
        self.assertFalse(ret['pending_tasks'][0] in subprocess.check_output(['sos', 'status']).decode())
        # test purge by status
        subprocess.call(['sos', 'purge', '--status', 'aborted'])
        self.assertFalse('killed' in subprocess.check_output(['sos', 'status', '-v', '3']).decode())
        # test purge by age
        subprocess.call(['sos', 'purge', '--age=-20s'])
        # purge by all is not tested because it is dangerous


    @unittest.skipIf('TRAVIS_OS_NAME' in os.environ, 'Test fails on travis for unknown reason #831')
    def testNoWait(self):
        '''Test no wait'''
        script = SoS_Script(r'''
[10]
input: for_each=[{'a': range(3)}]

task: concurrent=True
run:
    echo "a = ${a}"
    sleep 20
''')
        wf = script.workflow()
        #st = time.time()
        env.config['sig_mode'] = 'force'
        env.config['wait_for_task'] = False
        ret = Base_Executor(wf).run()
        # sos should quit
        self.assertGreater(len(ret['pending_tasks']), 0)
        #
        time.sleep(18)
        print('RESTART')
        env.config['sig_mode'] = 'default'
        env.config['wait_for_task'] = True
        env.config['resume_mode'] = True
        #st = time.time()
        try:
            Base_Executor(wf).run()
            # sos should wait till everything exists
            #self.assertLess(time.time() - st, 15)
        except SystemExit:
            # ok if the task has already been completed and there is nothing
            # to resume
            pass
        #
        # rerun task in different mode
        env.config['resume_mode'] = False
        env.config['wait_for_task'] = True
        Base_Executor(wf).run()
        env.config['sig_mode'] = 'assert'
        Base_Executor(wf).run()
        env.config['sig_mode'] = 'build'
        Base_Executor(wf).run()

    def testSharedOption(self):
        '''Test shared option of task'''
        FileTarget("a.txt").remove("both")
        FileTarget("a100.txt").remove("both")
        script = SoS_Script('''
[10: shared = {'a': 'a[0]'}]
task: shared={'a': 'int(open("a.txt").read())'}
run:
  echo 100 > a.txt

[20]
run:
    touch a${a}.txt
''')
        wf = script.workflow()
        Base_Executor(wf, config={'sig_mode': 'force'}).run()
        self.assertTrue(os.path.isfile("a100.txt"))
        # sequence of var or mapping
        FileTarget("a.txt").remove("both")
        FileTarget("a100.txt").remove("both")
        script = SoS_Script('''
[10: shared = {'a': 'a[0]', 'b':'b[0]'}]
task: shared=[{'a': 'int(open("a.txt").read())'}, 'b']
b = 20
run:
  echo 100 > a.txt

[20]
run:
    touch a${a}_${b}.txt
''')
        wf = script.workflow()
        Base_Executor(wf, config={'sig_mode': 'force'}).run()
        self.assertTrue(os.path.isfile("a100_20.txt"))

    def testTrunkSizeOption(self):
        '''Test option trunk_size'''
        with open('test_trunksize.sos', 'w') as tt:
            tt.write('''
[10]
input: for_each={'I': range(10)}
task: trunk_size=5, cores=1, mem='1M', walltime='10m'
run:
    echo ${I} > ${I}.txt
    sleep 2
''')
        wf = SoS_Script(filename='test_trunksize.sos').workflow()
        res = Base_Executor(wf, config={
                'wait_for_task': False,
                'sig_mode': 'force',
                'script': 'test_trunksize.sos',
                'max_running_jobs': 10,
                'bin_dirs': [],
                'workflow_args': [],
                'output_dag': '',
                'targets': [],
                'max_procs': 4,
                'default_queue': None,
                'workflow': 'default',
                'workdir': '.',
                }).run()
        self.assertEqual(len(res['pending_tasks']), 2)
        subprocess.call('sos resume -w', shell=True)
        for i in range(10):
            self.assertTrue(os.path.isfile('{}.txt'.format(i)))
            FileTarget('{}.txt'.format(i)).remove('both')
        FileTarget('test_trunksize.sos').remove()

    def testTrunkWorkersOption(self):
        '''Test option trunk_workers'''
        with open('test_trunkworker.sos', 'w') as tt:
            tt.write('''
[10]
input: for_each={'I': range(12)}
task: trunk_size=6, trunk_workers=3, mem='1M', walltime='10m'
run:
    echo ${I} > ${I}.txt
    sleep 2
''')
        wf = SoS_Script(filename='test_trunkworker.sos').workflow()
        res = Base_Executor(wf, config={
                'wait_for_task': False,
                'sig_mode': 'force',
                'script': 'test_trunkworker.sos',
                'max_running_jobs': 10,
                'bin_dirs': [],
                'workflow_args': [],
                'output_dag': '',
                'targets': [],
                'max_procs': 4,
                'default_queue': None,
                'workflow': 'default',
                'workdir': '.',
                }).run()
        self.assertEqual(len(res['pending_tasks']), 2)
        subprocess.call('sos resume -w', shell=True)
        for i in range(10):
            self.assertTrue(os.path.isfile('{}.txt'.format(i)))
            FileTarget('{}.txt'.format(i)).remove('both')
        FileTarget('test_trunkworker.sos').remove()

    def testTaskTags(self):
        '''Test option tags of tasks'''
        import random
        tag = "tag{}".format(random.randint(1, 100000))
        with open('test_tags.sos', 'w') as tt:
            tt.write('''
[10]
input: for_each={{'i': range(10)}}
task: tags='{}', trunk_size=2
sh:
  echo {} ${{i}}
'''.format(tag, tag))
        wf = SoS_Script(filename='test_tags.sos').workflow()
        res = Base_Executor(wf, config={
                'wait_for_task': False,
                'sig_mode': 'force',
                'script': 'test_trunkworker.sos',
                'max_running_jobs': 10,
                'bin_dirs': [],
                'workflow_args': [],
                'output_dag': '',
                'targets': [],
                'max_procs': 4,
                'default_queue': None,
                'workflow': 'default',
                'workdir': '.',
                }).run()
        ret = subprocess.check_output('sos status -t {}'.format(tag), shell=True).decode()
        self.assertEqual(len(ret.splitlines()), 5, "Obtained {}".format(ret))
        # test multiple tags
        tag1 = "tag{}".format(random.randint(1, 100000))
        tag2 = "tag{}".format(random.randint(1, 100000))
        with open('test_tags.sos', 'w') as tt:
            tt.write('''
[10]
input: for_each={{'i': range(2)}}
task: tags=['{}', '{}']
sh:
  echo {} ${{i}}
'''.format(tag1, tag2, tag1))
        wf = SoS_Script(filename='test_tags.sos').workflow()
        res = Base_Executor(wf, config={
                'wait_for_task': False,
                'sig_mode': 'force',
                'script': 'test_trunkworker.sos',
                'max_running_jobs': 10,
                'bin_dirs': [],
                'workflow_args': [],
                'output_dag': '',
                'targets': [],
                'max_procs': 4,
                'default_queue': None,
                'workflow': 'default',
                'workdir': '.',
                }).run()
        ret = subprocess.check_output('sos status -t {}'.format(tag2), shell=True).decode()
        self.assertEqual(len(ret.splitlines()), 2, "Obtained {}".format(ret))        


if __name__ == '__main__':
    unittest.main()
