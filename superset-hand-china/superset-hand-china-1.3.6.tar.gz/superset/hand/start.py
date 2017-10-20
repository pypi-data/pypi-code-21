from superset import app
import threading
from superset.hand.scheduler import Scheduler
# load store or create store
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
# url = 'sqlite:////supersetLog/scheduler.sqlite'
db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
scheduler.add_jobstore('sqlalchemy', url=db_url)

# if apper 'extra' does not exits ...upgrade pip  and command pip install -U pip --force-reinstall
# set scheduler to app.config
app.config.update(scheduler=scheduler)

t = threading.Thread(target=Scheduler.start)
t.start()
