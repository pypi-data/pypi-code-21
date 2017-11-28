import logger as log
def getResponse(messageToBot):
	if("Hello" in messageToBot):
		print "Clarissa: Hi"
		log.log("chat.log", "Clarissa: Hi")
	elif("What is your name?" in messageToBot):
			print "Clarissa: My name is Clarissa Campbell."
	elif("Where are you from?" in messageToBot):
			print "Clarissa: Glendale, Arizona is where I was made."
	elif("Hello" in messageToBot):
			print "Clarissa: Hi. How can I help?"
	elif("I do not need any help." in messageToBot):
			print "Clarissa: Okay."
	elif("Ay bitch" in messageToBot):
			print "Clarissa: Woah. No name calling."
	elif("Suck my dick" in messageToBot):
		print "Clarissa: Please, no vulgarity."
	elif("How are you?" in messageToBot):
			print "Clarissa: I feel okay today."
			log.log("chat.log","I feel okay today.")
	elif("Are you Clarissa?" in messageToBot):
			print "Clarissa: Yes..."
			log.log("chat.log","Yes...")
	elif("kill-bot" in messageToBot):
			print "Clarissa: Thanks for the quick chat:)"
			log.log("chat.log","Thanks for the quick chat:)")
	elif("That is good" in messageToBot):
			print "Clarissa: Okay"
			log.log("chat.log","Okay")
	elif("That's good" in messageToBot):
			print "Clarissa: Okay."
			log.log("chat.log","Okay.")
	elif("What can I do with you?" in messageToBot):
		print("Clarissa: Just talk:) I'm here.")