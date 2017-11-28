import logger as log
def getResponse(messageToBot):
	if("Hello" in messageToBot):
		print("Clarissa: Hi")
		log.log("chat.log", "Clarissa: Hi")
	elif("What is your name?" in messageToBot):
			print("Clarissa: My name is Clarissa Campbell.")
			log.log("chat.log","My name is Clarissa Campbell.")
	elif("Where are you from?" in messageToBot):
			print("Clarissa: Glendale, Arizona is where I was made.")
			log.log("chat.log","Glendale, Arizona is where I was made.")
	elif("I do not need any help." in messageToBot):
			print("Clarissa: Okay.")
			log.log("chat.log","Okay.")
	elif("Ay bitch" in messageToBot):
			print("Clarissa: Woah. No name calling.")
			log.log("chat.log","Woah. No name calling.")
	elif("Suck my dick" in messageToBot):
			print("Clarissa: Please, no vulgarity.")
			log.log("chat.log","Please, no vulgarity.")
	elif("How are you?" in messageToBot):
			print("Clarissa: I feel okay today.")
			log.log("chat.log","I feel okay today.")
	elif("Hi." in messageToBot):
			print("Clarissa: Hey.")
			log.log("chat.log","Hey.")
	elif("Are you Clarissa?" in messageToBot):
			print("Clarissa: Yes...")
			log.log("chat.log","Yes...")
	elif("kill-bot" in messageToBot):
		print("Clarissa: Thanks for the quick chat:)")
	elif("That's good" in messageToBot):
		print("Clarissa: Okay.")
	elif("That is good" in messageToBot):
		print("Clarissa: Okay")
	elif("That\'s good" in messageToBot):
		print("Clarissa: Okay.")