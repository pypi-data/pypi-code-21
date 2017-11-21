from . import settings


class DummyMessage(object):

	def __init__(self, user, title, body, **options):
		self.user = user
		self.title = title
		self.body = body
		self.data = options.get("data", {})
		self.read = options.get("read", False)

	def get_onesignal_data(self):
		return {
			"body": self.body,
			"data": self.data,
		}	