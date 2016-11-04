#!/usr/bin/python
# -*- coding: utf-8 -*-
# This is a Python script that lets you use a raspberry pi to water your plants
# The live implementation of the script is a modified ELC My First Talking Ted
#
# Start by importing the libraries we want to use

import time # This is the time library, we need this so we can use the sleep function
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import random
from picamera import PiCamera # need this to take pictures
from datetime import datetime
from twython import Twython # need this for tweeting
from twython import TwythonStreamer # need this for monitoring Twitter for commands
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0]))) # sets script working directory

# Import all our secret stuff from the auth.py file; you have to change the settings!!!
from auth import (
                  consumer_key,
                  consumer_secret,
                  access_token,
                  access_token_secret,
                  )

# Define some variables to be used later on in our script
logfile = 'gardenerbear_log.txt' # Define the location of the logfile
tweetsdb = 'tweets.txt' # Define the location of the tweets file
# Do we want emails or tweets, do we want log messages printed on screen
twitter_bot_active = 1 # 0 is inactive, 1 active
camera_active = 1 # 0 is inactive, 1 active
verbose = 1 # 0 is inactive, 1 active

def writelog(message):
    '''This function writes to a logfile, and if verbose is true, it will also print
        the message to the screen'''
    if verbose:print(message) # Check to see if we are in verbose mode, if so, print the message to the screen
    messagetolog = "%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(message))
    with open(logfile, "a+") as file: # Open the logfile for writing in append mode
        file.write(messagetolog) # Write the message to the file

# CPU temp function
def PiCPUtemp():
    cmd = '/opt/vc/bin/vcgencmd measure_temp'
    line = os.popen(cmd).readline().strip()
    temp = line.split('=')[1].split("'")[0]
    return temp

# Random tweeting function
def randomTweet(user_tweeted, water_status):
    try:
        api = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
        tweetsFile = open(tweetsdb,'r')
        tweetsList = tweetsFile.readlines()
        tweetsFile.close()
        randomChoice = random.randrange(len(tweetsList))
        cputemp = PiCPUtemp()
        if water_status == 'dry':
            message = "Dear @%s, %s BTW, I need watering and my CPU temp is %sºC" % (user_tweeted, tweetsList[randomChoice].rstrip('\n'), cputemp)
            log_message = "Tweeted %s" % message
            writelog(log_message)
        elif water_status == 'wet':
            message = "Dear @%s, %s BTW, I don't need watering and my CPU temp is %sºC" % (user_tweeted, tweetsList[randomChoice].rstrip('\n'), cputemp)
            sys.stdout.write("{} {}\n".format(len(message), message))
            log_message = "Tweeted %s" % message
            writelog(log_message)
        if camera_active:
            log_message = "%s Starting Camera" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writelog(log_message)
            camera = PiCamera()
            log_message = "%s Camera Started" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writelog(log_message)
            timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
            photo_path = 'photos/%s.jpg' % timestamp
            log_message = "%s Taking Picture" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writelog(log_message)
            camera.capture(photo_path)
            time.sleep(3)
            camera.close()
            log_message = "%s Closed Camera" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writelog(log_message)
            with open(photo_path, 'rb') as photo:
                response = api.upload_media(media=photo)
                api.update_status(media_ids=[response['media_id']], status=message)
                log_message = "%s Tweet Success" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                writelog(log_message)
        else:
            api.update_status(status=message)
            log_message = "%s Tweet Success" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writelog(log_message)
        return None
    except IOError:
        if camera_active: camera.close()
        return None
# Camera function
def takeapicture():
    if camera_active:
        log_message = "%s Starting Camera" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        writelog(log_message)
        camera = PiCamera()
        log_message = "%s Camera Started" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        writelog(log_message)
        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        photo_path = 'photos/%s.jpg' % timestamp
        log_message = "%s Taking Picture" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        writelog(log_message)
        camera.capture(photo_path)
        time.sleep(3)
        camera.close()
        log_message = "%s Closed Camera" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        writelog(log_message)
try:
    takeapicture()

except KeyboardInterrupt:
    GPIO.cleanup()
    if camera_active: camera.close()
    file.close()
