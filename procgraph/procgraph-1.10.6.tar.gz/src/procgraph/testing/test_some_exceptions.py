#from .utils import PGTestCase



# class SemanticsTest(PGTestCase):
#     
#     def testBadExamples(self):
#         for example in bad_examples2:
#             self.check_semantic_error(example) 
#             
#     def testExamples(self):
#         for example in good_examples2:
#             self.check_semantic_ok(example)
# 
#      
# class ParamsTest(PGTestCase):
#     
#     def test1(self):
#         ''' Checking that we signal unused parameters. '''
# 
#         model_desc = """
#            |input name=x| -> |g1:gain| -> |output name=y|
#         """
#         # g2.gain is unused
#         self.assertRaises(SemanticError, model_from_string,
#                           model_desc, config={'g2.k': 2})
#        
