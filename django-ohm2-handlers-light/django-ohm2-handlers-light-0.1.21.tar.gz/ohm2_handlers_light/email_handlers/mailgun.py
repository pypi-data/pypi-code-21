from ohm2_handlers_light.definitions import EmailHandler
import requests, time

class Mailgun(EmailHandler):


	def __init__(self, domain, key, **kwargs):
		super(Mailgun, self).__init__(*(), **kwargs)

		self.MAILGUN_DOMAIN_NAME = domain
		self.MAILGUN_API_KEY = key
		self.auth = ("api", self.MAILGUN_API_KEY)
		address = kwargs.get("address", None)
		if address:
			self.address = address
		else:
			self.address = 'https://api.mailgun.net/v3/' + self.MAILGUN_DOMAIN_NAME + "/messages"	

		
	
	def send(self, tries = 2, delay = 0.1):
		data = {
			'from' : self.from_email,
			'to' : self.to_email,
			'subject' : self.subject,
			'html' : self.content,
		}

		for x in range(tries):
			
			try:
				res = requests.post(self.address, auth = self.auth, data = data)
			except Exception as e:
				res = None
			
			if res != None and res.status_code == 200:
				r = res.json()
				
				
				return True
			
			time.sleep(delay)
		return False	