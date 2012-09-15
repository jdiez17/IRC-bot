# -*- coding: utf-8 -*-
from module import Module
import redis
import tweepy
import sys
import time

class TwIRC(Module, tweepy.StreamListener):
    def __init__(self):
        self.modname = "Twitter <-> IRC bridge"
        self.r = redis.Redis()
        self.last_tweet = 0
        self.last_tweet_attempt = 0
        self.tweet_timeout = 10
        self.stream = None
        
        self.commands = dict()
        self.add_command(".tweet", self.tweet)
        
        self.twitter_user = "fearn0de"
        self.status_link = "http://twitter.com/" + self.twitter_user + "/status/%s"
        
        self.twitter_connect()
        
    def twitter_connect(self):
        ckey = self.r.get('fearnode.consumer.key')
        csecret = self.r.get('fearnode.consumer.secret')

        if not ckey or not csecret:
            print "Misconfigured!\n"
            ckey = raw_input("Consumer key: ")
            csecret = raw_input("Consumer secret: ")

            try:
                self.r.set('fearnode.consumer.key', ckey)
                self.r.set('fearnode.consumer.secret', csecret)
            except:
                print "Redis error."
                sys.exit()

        auth = tweepy.OAuthHandler(ckey, csecret)

        clientkey = self.r.get('fearnode.client.accesskey')
        clientsecret = self.r.get('fearnode.client.secret')

        if not clientkey or not clientsecret:
            print "OAuth wizard. Here be dragons.\n"

            try:
                    print "Authorize at " + auth.get_authorization_url()
            except tweepy.TweepError:
                    print "Could not fetch authorization url. Abort."
                    sys.exit()

            code = raw_input("Pin: ")

            try:
                auth.get_access_token(code)
            except tweepy.TweepError:
                print "Could not fetch access tokens. Invalid pin?"
                sys.exit()

            clientkey = auth.access_token.key
            clientsecret = auth.access_token.secret
                    
            try:
                    self.r.set('fearnode.client.accesskey', clientkey)
                    self.r.set('fearnode.client.secret', clientsecret)
            except:
                    print "Redis error."
                    sys.exit()

        auth.set_access_token(clientkey, clientsecret)
        self.api = tweepy.API(auth)
        
    def tweet(self, msg, cmd, user, arg):
        diff = time.time() - self.last_tweet
        if diff > self.tweet_timeout:
            try:
                res = self.api.update_status(' '.join(arg))
                self.last_tweet = time.time()
                
                #if time.time() - self.last_tweet_attempt < 5:
                #   return self.generate_response(
                
                return self.send_message(' '.join(arg) + " " + self.status_link % str(res.id))
            except Exception, e:
                return self.send_message(str(e))
        else:
            return self.send_message("espérate " + str(int(round(self.tweet_timeout - diff))) + " segundos, judío")
        
        self.last_tweet_attempt = time.time()
