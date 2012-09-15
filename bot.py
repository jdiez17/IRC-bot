# -*- coding: utf-8 -*-

import ConfigParser
from straight.plugin import load
from ircbot import IRCBot

if __name__ == '__main__':
    from modules.module import Module
    
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.ini'))
    
    bot = IRCBot()
    bot.set_config(config)
    
    plugins = [plugin_class() for plugin_class in load("modules", Module)]
    for plugin in plugins:
        bot.load_module(plugin)
    bot.end_load_modules()
    
    bot.connect(config.get('core', 'server'), int(config.get('core', 'port')))
