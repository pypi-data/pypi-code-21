import datetime
import logging

from tcell_agent.agent import TCellAgent


LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def end_timer(request):
    endtime = datetime.datetime.now()
    if request._tcell_context.start_time != 0:
        request_time = int((endtime - request._tcell_context.start_time).total_seconds() * 1000)
        TCellAgent.request_metric(
            request._tcell_context.route_id,
            request_time,
            request._tcell_context.remote_addr,
            request._tcell_context.user_agent,
            request._tcell_context.session_id,
            request._tcell_context.user_id
        )
        LOGGER.debug("request took %s", request_time)


def start_timer(request):
    request._tcell_context.start_time = datetime.datetime.now()
