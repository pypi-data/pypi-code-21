from procgraph.core.model_loader import model_from_string

from .utils import PGTestCase


class NamingTest(PGTestCase):
    
    def test_correct_naming(self):
        # in all these cases, the identity block should have
        # the output signal named "x"
        examples = [
        " |input name=x| -> |identity| ",
        " |input name=y| -> x -> |identity| ",
        """
          |i0:input name=y| -> x 
          
          x -> |identity| 
        """,
                    
        """
          |i0:input name=y| 
          
          i0.y[x] -> |identity| 
        """
                    
        ]
        
        for example in examples:
            self.try_one(example)
        
    def try_one(self, example):
        model = model_from_string(example)
        block = model.name2block['identity']
        names = block.get_output_signals_names()
        print "Obtained %s from '''%s'''" % (names, example)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], 'x')
        
        
