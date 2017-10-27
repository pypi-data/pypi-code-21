from tcell_agent.agent.agent_threads import TCellAgent
from tcell_agent.appsensor.manager import app_sensor_manager
from tcell_agent.config import configuration
import tcell_agent


def just_return(self):
    return


TCellAgent.ensure_polling_thread_running = just_return
TCellAgent.ensure_metrics_pipe_thread_running = just_return
TCellAgent.ensure_fork_pipe_thread_running = just_return
TCellAgent.ensure_event_handler_thread_running = just_return

app_sensor_manager.use_threads = False

configuration.WARN_TO_CONSOLE = False

from tcell_agent.instrumentation.djangoinst import app
app._started = True
app._route_table_sent = True
