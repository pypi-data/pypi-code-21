
from time import sleep

from unicon.eal.dialogs import Statement

from .patterns import VosPatterns

p = VosPatterns()


def paginate(spawn, context, session):
    """ paginating """
    m = spawn.match.last_match
    begin_page_line = m.group(1)
    end_page_line = m.group(2)
    total_lines = m.group(3)

    if (end_page_line == total_lines) or (int(end_page_line) >= context.get('lines', 100)):
      spawn.send('q')
    else:
      spawn.send('n')

def press_enter(spawn):
    sleep(.02)
    spawn.send(' ')


paginate_stmt = \
    Statement(pattern=p.paging_options,
      action=paginate,
      args=None,
      loop_continue=True,
      continue_timer=True)

press_enter_space_q_stmt = \
    Statement(pattern=p.press_enter_space_q,
              action=press_enter,
              args=None,
              loop_continue=True,
              continue_timer=True)

vos_statement_list = [
    press_enter_space_q_stmt,
    paginate_stmt
]

