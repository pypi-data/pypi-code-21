from .utils import PGTestCase


class TestRenaming(PGTestCase):
    def test_renaming(self):
        ''' Sometimes instancing a block twice will give error because
            we overwrote the parsed spec. '''
        model_spec = """
--- model loaders

|input name=y|  --> |identity| --> y_dot
y_dot  --> |identity| --> y_ddot
 
         """
        self.check_semantic_ok(model_spec)
