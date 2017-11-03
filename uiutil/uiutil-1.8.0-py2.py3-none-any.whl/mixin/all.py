
from var import VarMixIn
from poll import PollMixIn
from style import StyleMixIn
from widget import WidgetMixIn
from layout import FrameLayoutMixIn
from classutils.observer import ObserverMixIn
from classutils.thread_pool import ThreadPoolMixIn


class AllMixIn(FrameLayoutMixIn,
               StyleMixIn,
               WidgetMixIn,
               VarMixIn,
               PollMixIn,
               ThreadPoolMixIn,
               ObserverMixIn):

    def __init__(self,
                 *args,
                 **kwargs):

        super(AllMixIn, self).__init__(*args, **kwargs)
