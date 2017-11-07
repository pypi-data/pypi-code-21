from django.db import models

class UserAgent(models.Model):
	string = models.TextField(unique=True)
	visits = models.PositiveIntegerField(default=0,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.string
	
	@property
	def short_agent(self):
		if len(self.string) > 40:
			return "{}...".format(self.string[:40])
		else:
			return self.string
		
	def increment(self):
		self.visits += 1
		
	def save(self, *args, **kwargs):
		self.increment()
		super(UserAgent, self).save(*args, **kwargs)
	
class Ip(models.Model):
	address = models.CharField(max_length=50,unique=True)
	visits = models.PositiveIntegerField(default=0,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.address
		
	def increment(self):
		self.visits += 1
		
	def save(self, *args, **kwargs):
		self.increment()
		super(Ip, self).save(*args, **kwargs)
	
class Path(models.Model):
	path = models.CharField(max_length=400,unique=True)
	visits = models.PositiveIntegerField(default=0,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.path
	
	def increment(self):
		self.visits += 1
	
	@property
	def short_path(self):
		if len(self.path) > 40:
			return "{}...".format(self.path[:40])
		else:
			return self.path
		
	def save(self, *args, **kwargs):
		self.increment()
		super(Path, self).save(*args, **kwargs)

class Visit(models.Model):
	useragent = models.ForeignKey(UserAgent)
	ip = models.ForeignKey(Ip)
	path = models.ForeignKey(Path)
	method = models.CharField(max_length=10,blank=True)
	content_type = models.CharField(max_length=256,blank=True)
	encoding = models.CharField(max_length=265,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return "{0} - {1} - {2}".format(
			self.useragent.short_agent, 
			self.ip, 
			self.path.short_path,
		)
