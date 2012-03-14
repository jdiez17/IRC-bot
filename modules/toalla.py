from module import Module
import time
import random

class Toalla(Module):
	def __init__(self):
		self.modname = "ToallaBot"
		self.last_toalla = 0
		self.toalla_timeout = 5
		
	def parse(self, msg, cmd, user, arg):
		if self.nick.lower() in cmd.lower():
			return self.recursion_no_message(".toalla", user, [user])
		elif ".toalla" == cmd:
			toallas = open('/usr/share/toalla.txt')
			override = self.is_admin(user)
			diff = time.time() - self.last_toalla
			
			if diff < self.toalla_timeout and not override:
				self.ignore()
			
			toa_list = [] 
			

			try:
				times = int(arg[0])
				
				if times > 22:
					return self.send_message("Y una mierda.")
				if times == 0:
					return self.ignore()
					
				nick = ' '.join(arg[1:])
			except:
				times = 1
				nick = ' '.join(arg[0:])

			if nick[:1] == "@":
				times = 1
				tollatweet = True
			else:
				tollatweet = False
				
			if self.is_admin(nick):
				return self.send_message("No.")

			for toalla in toallas:
				this_toalla = toalla.replace("\n", "")
				this_toalla = this_toalla.replace("$1-", nick)
				this_toalla = this_toalla.replace("$me", self.nick)
				this_toalla = this_toalla.replace("$network", "#fearnode") # fix hardcode

				toa_list.append(this_toalla)

			the_toalla = random.choice(toa_list)
			while "$nick" in the_toalla or (len(the_toalla) > 140 and tollatweet):
				the_toalla = random.choice(toa_list)
				
			if tollatweet:
				return self.recursion_no_message(".tweet", user, [the_toalla])
			else:
				if times > 1:
					return self.recursion_with_message(the_toalla, ".toalla", user, [times-1, nick])
				else:
					return self.send_message(the_toalla)
			self.last_toalla = time.time()
		else:
			return self.ignore()
	