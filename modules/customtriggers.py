from module import Module
import redis
import re

class CustomTriggers(Module):
    def __init__(self):
        self.modname = "Custom Triggers"
        self.commands = dict()
        self.r = redis.Redis()
        
        self.add_command(".remember", self.add_trigger)
        self.add_command(".forget", self.del_trigger)
        self.add_command(".list_triggers", self.list_triggers)
        
    def _clean(self, str):
        return str.replace(' ', '_')
    
    def add_trigger(self, cmd, msg, user, arg):
        trigger, message = ' '.join(arg).split(' = ')
        
        if not trigger:
            return self.ignore()
        
        try:
            self.r.sadd("ircbot_triggers", trigger)
            self.r.set("ircbot_trigger_" + self._clean(trigger), message)
        except Exception, e:
            return self.send_message(str(e))
        
        return self.send_message(trigger + " = " + message)
    
    def del_trigger(self, cmd, msg, user, arg):
        if not self.is_admin(self.get_username(user)):
            return self.ignore()
            
        trigger = ' '.join(arg)
        
        try:
            self.r.srem("ircbot_triggers", trigger)
            self.r.delete("ircbot_trigger_" + self._clean(trigger))
        except Exception, e:
            return self.send_message(str(e))
    
        return self.send_message(trigger + " trigger deleted.")
        
    def list_triggers(self, cmd, msg, user, arg):   
        triggers = self.r.smembers("ircbot_triggers")
        
        return self.send_message(', '.join(triggers))
    
    def parse_custom(self, msg, cmd, user, arg):
        triggers = self.r.smembers("ircbot_triggers")
            
        for trigger in triggers:
            if trigger in msg:
                answer = self.r.get("ircbot_trigger_" + self._clean(trigger))
                answer = answer.replace("%user", self.get_username(user))
                return self.send_message(answer)
        