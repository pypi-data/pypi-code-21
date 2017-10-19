from .utils import PGTestCase
 
good_examples = [
"""
type = generic_in0_out1

|$type | --> X
""",
"""
type = gen

|"${type}eric_in0_out1"| --> X
"""

            
]
     
     
bad_examples = [

"""

|"${type}eric_in0_out1"| --> X
"""
                
]   
    

class DynamicBlocksTest(PGTestCase):
    
    def testGoodExamples(self):
        for example in good_examples:
            self.check_semantic_ok(example)
                        
    def testBadExamples(self):
        for example in bad_examples:
            self.check_semantic_error(example)
