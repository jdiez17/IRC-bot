from module import Module
import redis

class CustomTriggers(Module):
	def __init__(self):
		self.modname = "Custom Triggers"
		self.commands = dict()
		self.r = redis.Redis()
		
		self.add_command(".remember", self.add_trigger)
		self.add_command(".forget", self.del_trigger)
		
	def _clean(self, str):
		return str.replace(' ', '_')
	
	def add_trigger(self, cmd, msg, user, arg):
		trigger, message = ' '.join(arg).split(' = ')
		
		try:
			self.r.sadd("ircbot_triggers", trigger)
			self.r.set("ircbot_trigger_" + self._clean(trigger), message)
		except Exception, e:
			return self.send_message(str(e))
		
		return self.send_message(trigger + " = " + message)
	
	def del_trigger(self, cmd, msg, user, arg):
		trigger = ' '.join(arg)
		
		try:
			self.r.srem("ircbot_triggers", trigger)
			self.r.delete("ircbot_trigger_" + self._clean(trigger))
		except Exception, e:
			return self.send_message(str(e))
	
		return self.send_message(trigger + " trigger deleted.")
		
	def parse_custom(self, cmd, msg, user, arg):
		triggers = self.r.smembers("ircbot_triggers")
		
		if(len(arg) > 0):
			msg = ' '.join(arg)
			
		for trigger in triggers:
			if trigger in msg or trigger == cmd:
				return self.send_message(self.r.get("ircbot_trigger_" + self._clean(trigger)))
		