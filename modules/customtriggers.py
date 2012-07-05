from module import Module
import redis

class CustomTriggers(Module):
	def __init__(self):
		self.modname = "Custom Triggers"
		self.commands = dict()
		self.r = redis.Redis()
		
		self.add_command(".trigger", self.add_trigger)
		self.add_command(".deltrigger", self.del_trigger)
		
	def add_trigger(self, cmd, msg, user, arg):
		trigger = arg[0]
		message = ' '.join(arg[1:])
		
		try:
			self.r.sadd("ircbot_triggers", trigger)
			self.r.set("ircbot_trigger_" + trigger, message)
		except:
			return self.send_message("Redis error.")
		
		return self.send_message(trigger + " = " + message)
	
	def del_trigger(self, cmd, msg, user, arg):
		trigger = arg[0]
		
		try:
			self.r.srem("ircbot_triggers", trigger)
			self.r.delete("ircbot_trigger_" + trigger)
		except:
			return self.send_message("Trigger not found.")
	
		return self.send_message(trigger + " trigger deleted.")
		
	def parse_custom(self, cmd, msg, user, arg):
		triggers = self.r.smembers("ircbot_triggers")
		if cmd in triggers:
			return self.send_message(self.r.get("ircbot_trigger_" + cmd))
		