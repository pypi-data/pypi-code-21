__version__ = '0.2.0'


from aionationstates.world_ import World
world = World()


from aionationstates.nation_ import Nation
from aionationstates.nation_control import NationControl
def nation(name, *, autologin='', password=''):
    return (NationControl(name, autologin, password)
            if autologin or password else Nation(name))


from aionationstates.region_ import Region
region = Region


from aionationstates.session import set_user_agent, ApiQuery

from aionationstates.types import *
from aionationstates.ns_to_human import *
from aionationstates.happenings import *

from aionationstates.utils import datetime_to_ns, normalize
