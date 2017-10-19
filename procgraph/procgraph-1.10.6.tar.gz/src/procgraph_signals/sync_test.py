from procgraph import (Generator, Block, ModelExecutionError,
    register_model_spec)
from procgraph.core.registrar import default_library
from procgraph.testing.utils import PGTestCase


examples = [
("If coincident, output that",
"""
1 2 3 4 5 6 7 8 9 
1 2 3 4 5 6 7 8 9
1 2 3 4 5 6 7 8 9 
"""),
("Skip additional",
"""
1 2 3 4 5 6 7 8 9 
1*2*3*4*5*6*7*8*9
1 2 3 4 5 6 7 8 9 
"""),
("Wait for the next.",
"""
1 2 3 4 5 6 7 8 9 
 1 2 3 4 5 6 7 8 9
 1 2 3 4 5 6 7 8 9
"""),

("Skip first one if necessary",
"""
 1 2 3 4 5 6 7 8 9 
* 1 2 3 4 5 6 7 8 9
* 1 2 3 4 5 6 7 8 9
"""),
("Wait for the next  (multiple delay).",
"""
1   2   3   4   5   6   7   8   9 
 1   2   3   4   5   6   7   8   9
  1   2   3   4   5   6   7   8   9
"""),
("Skip master if signals don't arrive .",
"""
1  *2  *3  **4***5**6   7   8   9 
 1   2   3   4   5   6   7   8   9
 1   2   3   4   5   6   7   8   9
"""),
("Skip slave if other slave doesn't arrive.",
"""
1   2   3   4   5   6   7   8   9 
 1*  2   3   4   5   6   7   8   9
  1   2   3   4   5   6   7   8   9
"""),
("Skip slave if other slave doesn't arrive.",
"""
* 1   2   3   4   9  
 1   *   2   3   4   9
   1   2   3   4   9
"""),
]

register_model_spec('''
--- model sync_test

|log_sim line=$master| -> master 
|log_sim line=$slave1| -> slave1
|log_sim line=$slave2| -> slave2

master, slave1, slave2 -> |sync2| -> |check_sync| --> |output name=value|

''')


class LogSim(Generator):
    Block.alias('log_sim')

    Block.output('stream')

    def init(self):
        line = self.config.line

        self.queue = []
        for i, char in enumerate(line):
            t = i + 1
            if char == ' ':
                continue
            elif char == '*':
                self.queue.insert(0, (t, -1))
            elif char.isdigit():
                v = int(char)
                self.queue.insert(0, (t, v))
            else:
                raise Exception('Bad input "%s" at char %d of "%s".' % \
                                (char, t, line))

    def next_data_status(self):
        if self.queue:
            return (True, self.queue[-1][0])
        else:
            return (False, None)

    def update(self):
        assert self.queue
        timestamp, value = self.queue.pop()
        self.set_output(0, value, timestamp)


class CheckSync(Block):
    Block.alias('check_sync')
    Block.output('value')

    def update(self):

        values = self.get_input_signals_values()
        timestamps = self.get_input_signals_timestamps()

        ok = True
        for v in values:
            if v is None or  v != values[0]:
                ok = False
        for t in timestamps:
            if t is None or t != timestamps[0]:
                ok = False

        if not ok:
            msg = 'Received bad inputs. Timestamps: %s Values: %s ' % \
                    (timestamps, values)

            raise ModelExecutionError(msg, self)

        self.output.value = values[0]


class TestSync(PGTestCase):

    def not_working(self):

        for description, example in examples:
            print "Trying with: %s" % description
            # get non-empty lines
            lines = filter(lambda x: x.strip(), example.split('\n'))
            print lines
            assert len(lines) == 3
            config = {'master': lines[0],
                      'slave1': lines[1],
                      'slave2': lines[2]}

            model = default_library.instance('sync_test', name=None,
                                             config=config)

            model.init()
            while model.has_more():
                model.update()
            model.finish()

            final = model.get_output(0)
            if final != 9:
                raise Exception('expected final output to be 9, not %s'
                                % final)



