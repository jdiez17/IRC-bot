from module import Module
import sys
from subprocess import Popen, PIPE

class AdminCommands(Module):
	def __init__(self):
		self.modname = "Admin Commands"
		
	def parse_raw(self, line):
		if "ERROR :Closing Link:" in line:
			return self.reconnect()
			
		if "INVITE " + self.nick in line:
			return self.send_raw_message("JOIN " + self.config.get('core', 'home_channel'))
		else:
			return self.ignore()
	
	def parse(self, msg, cmd, user, arg):
		if not self.is_admin(user):
			return self.ignore()
			
		if cmd == ".rehash":
			return self.reconnect()
			
		if cmd == ".lock":
			return self.acquire_lock()
			
		if cmd == ".unlock":
			return self.release_lock();
			
		if cmd == ".gitupdate":
			proc = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE)
			code = proc.wait()
			if code == 0:
				proc_msg = proc.stdout.read()
				if "Already up-to-date." in proc_msg:
					return self.send_message("No updates found.")
					
				return self.send_message("Updated.")
		if cmd == ".parrot":
			msg = msg.replace(cmd + " ", "")
			return self.send_message(msg)
			
		if cmd == ".join":
			return self.send_raw_message("JOIN " + arg[0])
			
		else:
			return self.ignore()
		