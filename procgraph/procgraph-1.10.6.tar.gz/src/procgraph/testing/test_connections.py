from ..core.exceptions import SemanticError
from ..core.model_loader import model_from_string # XXX:

from .utils import PGTestCase

good_examples2 = [
""" |constant value=2| -> [0] res """,

""" # Multiple inputs
|constant value=12| -> a
|constant value=13| -> b
a, b -> |+| -> c  """,

""" # Multiple inputs / anonymous
|constant value=12| -> a -> |gain k=3| -> c
|constant value=13| -> |gain k=-1| -> d
 c, d -> |+| -> result         """,

""" # Referring to outputs using numbers  
|constant value=12| -> [0]a  """,

""" # Referring to input/outputs using numbers  
|constant value=12| -> [0]a[0] -> |gain k=1|  """,

""" # A block by itself should be fine  
|generic_in0_out0|  
|generic_in0_out2|  """,
 
""" # Trying some named connections (1)  
|generic_in0_out1| -> |generic_in1_out0|  """,

""" # Trying some named connections (1)
# Should be the same  
|generic_in0_out1| -> x
x -> |generic_in1_out0|  """,

"""# Should be the same  as well
|c1:constant value=1| -> |g1:generic_in1_out1|
g1.0 -> |g2:generic_in1_out0|  """,

"""# Should be the same  as well
|g1:generic_in0_out1|
g1.0 -> |g2:generic_in1_out0|  """ 

]

bad_examples2 = [
""" # Bad number of outputs  
|constant value=12| -> a, b  """,

""" # Bad output name  
|constant value=12| -> [inexistent]a  """,

""" # Bad output number  
|constant value=12| -> [1]a  """,

""" # inexistent input
invalid -> |gain k=2|            """,

""" # input to something with no input
|constant value=12| -> a
a -> |constant value=12|   """,

""" # wrong number of inputs
|constant value=12| -> a
|constant value=12| -> b
a, b -> |gain k=1|              """,

""" # Cannot use output if terminating  
|constant value=12| -> [0]a[0]  """,

""" # Incompatible signals (anonymous) 
|constant value=12| -> |generic in=2 out=1| -> y """,

""" # We don't want to connect blocks with no signals  
|generic in=0 out=0| -> |generic in=0 out=2|  """,
 
""" # It cannot be without input if one is needed   
|generic in=1 out=0|  """,
 
""" # Double definition   
|generic_in0_out1| -> a  
|generic_in0_out1| -> a""",


""" # Oops, definition is left dangling...   
|generic_in0_out1| -> a  
|generic_in0_out1| -> a
g1.in = 2
""",

]


class SemanticsTest(PGTestCase):
    
    def testBadExamples(self):
        for example in bad_examples2:
            self.check_semantic_error(example) 
            
    def testExamples(self):
        for example in good_examples2:
            self.check_semantic_ok(example)

     
class ParamsTest(PGTestCase):
    
    def test1(self):
        ''' Checking that we signal unused parameters. '''

        model_desc = """
           |input name=x| -> |g1:gain| -> |output name=y|
        """
        # g2.gain is unused
        self.assertRaises(SemanticError, model_from_string,
                          model_desc, config={'g2.k': 2})
       

    
