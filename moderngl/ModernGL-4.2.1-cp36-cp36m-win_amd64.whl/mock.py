'''
    Mock linters.
'''

# pylint: skip-file

__all__ = ['mgl', 'Error']


class Error(Exception):
    '''
        ModernGL Error
    '''


class MockObject:
    '''
        MockObject
    '''

    wrapper = None
    mglo = None


class Implementation:
    '''
        Implementation
    '''

    BLEND = MockObject()
    DEPTH_TEST = MockObject()
    CULL_FACE = MockObject()
    ENABLE_MASK = MockObject()

    LINEAR = MockObject()
    NEAREST = MockObject()
    MIPMAP = MockObject()

    TRIANGLES = MockObject()
    TRIANGLE_STRIP = MockObject()
    TRIANGLE_FAN = MockObject()
    LINES = MockObject()
    LINE_STRIP = MockObject()
    LINE_LOOP = MockObject()
    POINTS = MockObject()
    LINE_STRIP_ADJACENCY = MockObject()
    LINES_ADJACENCY = MockObject()
    TRIANGLE_STRIP_ADJACENCY = MockObject()
    TRIANGLES_ADJACENCY = MockObject()

    def create_context(self) -> 'Context':
        '''
            create_context
        '''

    def create_standalone_context(self, *args) -> 'Context':
        '''
            create_standalone_context
        '''


mgl = Implementation()
