from module import Module
import sys
from subprocess import Popen, PIPE

class AdminCommands(Module):
    def __init__(self):
        self.modname = "Admin Commands"
        self.commands = dict()
        
        self.add_command(".rehash", self.rehash)
        self.add_command(".lock", self.lock)
        self.add_command(".unlock", self.unlock)
        self.add_command(".gitupdate", self.gitupdate)
        self.add_command(".parrot", self.parrot)
        
    def parse_raw(self, line):
        if "ERROR :Closing Link:" in line:
            return self.reconnect()
            
        if "INVITE " + self.nick in line:
            channel = line.split(":")[2]
            return self.send_raw_message("JOIN " + channel)
        else:
            return self.ignore()
    
    def rehash(self, msg, cmd, user, arg):
        if not self.is_admin(user):
            return self.ignore()
        return self.reconnect()
    
    def lock(self, msg, cmd, user, arg):
        if not self.is_admin(user):
            return self.ignore()
        return self.acquire_lock()
    
    def unlock(self, msg, cmd, user, arg):
        if not self.is_admin(user):
            return self.ignore()
        return self.release_lock()
    
    def gitupdate(self, msg, cmd, user, arg):
        proc = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE)
        code = proc.wait()
        if code == 0:
            proc_msg = proc.stdout.read()
            if "Already up-to-date." in proc_msg:
                return self.send_message("No updates found.")
                
            return self.send_message("Updated.")
    
    def parrot(self, msg, cmd, user, arg):
        if not self.is_admin(user):
            return self.ignore()
        msg = msg.replace(cmd + " ", "")
        return self.send_message(msg)
        
