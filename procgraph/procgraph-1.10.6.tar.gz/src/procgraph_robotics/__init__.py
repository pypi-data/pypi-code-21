''' 

    Some functions specific to robotics applications. 

    Requires: http://github.com/AndreaCensi/geometry
    
'''


procgraph_info = {
    # List of python packages 
    'requires': ['geometry']
}

# Smart dependency resolution
from procgraph import import_magic, import_succesful
geometry = import_magic(__name__, 'geometry')

if import_succesful(geometry):
    from . import pose2velocity
    from . import laser_display
    from . import laser_dot_display
    from . import organic_scale
    from . import misc
    from . import pose2velocity_b
