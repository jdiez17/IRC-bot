from module import Module
import sys
from subprocess import Popen, PIPE
from decorators import admincommand

class AdminCommands(Module):
    def __init__(self):
        self.modname = "Admin Commands"
        self.commands = dict()
        
        self.add_command(".rehash", self.rehash)
        self.add_command(".lock", self.lock)
        self.add_command(".unlock", self.unlock)
        self.add_command(".gitupdate", self.gitupdate)
        self.add_command(".parrot", self.parrot)
        self.add_command(".join", self.join)
        
    def parse_raw(self, line):
        if "ERROR :Closing Link:" in line:
            return self.reconnect()
            
        if "INVITE " + self.nick in line:
            channel = line.split(":")[2]
            return self.send_raw_message("JOIN " + channel)
        else:
            return self.ignore()
    
    
    @admincommand
    def rehash(self, msg, cmd, user, arg):
       return self.reconnect()

    @admincommand    
    def lock(self, msg, cmd, user, arg):
       return self.acquire_lock()

    @admincommand    
    def unlock(self, msg, cmd, user, arg):
       return self.release_lock()
    
    def gitupdate(self, msg, cmd, user, arg):
        proc = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE)
        code = proc.wait()
        if code == 0:
            proc_msg = proc.stdout.read()
            if "Already up-to-date." in proc_msg:
                return self.send_message("No updates found.")
                
            return self.send_message("Updated.")

    @admincommand
    def join(self, msg, cmd, user, arg):
        return self.send_raw_message("JOIN " + arg[0])
 
    @admincommand   
    def parrot(self, msg, cmd, user, arg):
        msg = msg.replace(cmd + " ", "")
        return self.send_message(msg)
        
