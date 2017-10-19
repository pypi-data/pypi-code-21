from ..core.model_loader import model_from_string

from .utils import PGTestCase

examples = [
""" # direct
   |input name=x| -> |g1:gain| -> |output name=y|
""",
""" # named
   |input name=x| -> v -> |g1:gain| -> |output name=y|
""",
""" # named
   |input name=x| -> v -> |g1:gain| -> y -> |output name=y|
""",
""" # only  identity 2
   |input name=x| -> |identity| -> |g1:gain| -> |identity| -> |output name=y|
""",
""" # named + identity
   |input name=x| -> v -> |identity| -> |g1:gain| -> y -> |output name=y|
""",
""" # named + identity
   |input name=x| -> |identity| -> v -> |g1:gain| -> y -> |output name=y|
""",
""" # only  identity
   |input name=x| -> |identity| -> |g1:gain| -> y -> |output name=y|
""",
""" 
   (x) -> |g1:gain| -> (y)
""",

]


class PipelineTest(PGTestCase):
    
    def test_pipeline(self):
        ''' All graphs equivalent (multiply by a gain), but interconnections
            change. '''
        for example in examples:
            self.try_one(example)
    
    def try_one(self, model_desc):
        print("Trying with '''%s'''" % model_desc)
        gain = 3
        model = model_from_string(model_desc, config={'g1.k': gain})
        model.init()
        
        for i in range(5):
            value = i
            timestamp = 4 + i * 0.5 
            model.from_outside_set_input('x', value, timestamp=timestamp)
            
            self.assertTrue(model.has_more())
            while model.has_more():
                print("update %s  y = %s" % (i, model.get_output(0)))
                model.update()

            self.assertEqual(model.get_output(0), gain * value)
            self.assertEqual(model.get_output_timestamp(0), timestamp)

