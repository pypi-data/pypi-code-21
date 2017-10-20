#################
#
# This file requires you to install endpoints to use
# install with `pip install endpoints`
# to run this server, use the command: `endpoints --prefix=controller --host=<hostname>:<port>`
#
#################

from endpoints import Controller

class Default(Controller):

  def POST(self, **kwargs):
    print(kwargs) #replace with the function that must consume the output
    return 'OK'

  def GET(self, **kwargs):
    print(kwargs) #replace with the function that must consume the output
    return 'OK' 