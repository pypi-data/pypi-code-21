from IPython import embed
from brewer.controller import Controller
from brewer.slack import BrewerBot
from brewer.version import VERSION

controller = Controller()
bot = BrewerBot()

print(("Brewer version %s" % VERSION))

embed()
