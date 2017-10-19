from ..core.model_loader import model_from_string

from .utils import PGTestCase


class DelayedTest(PGTestCase):

    def test_delayed(self):

        model_desc = """
           |generic_in0_out3| -> |identity| -> |identity| -> |block1:identity|
        """
        model = model_from_string(model_desc)

        block1 = model.name2block['block1']
        self.assertTrue(block1.are_output_signals_defined())

        print block1

# XXX: what's the deal here?
#  
#    def test_check_definitions(self):
#        
#        model_desc = """ 
#            |DoesNotDefineOutput|
#        """
#        
#        self.check_semantic_error(model_desc)
#        
#        
#        model_desc = """ 
#            |DoesNotDefineInput|
#        """
#        self.check_semantic_error(model_desc)

