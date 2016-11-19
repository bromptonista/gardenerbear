#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 0.9.7
# This is a Python script that lets you use a raspberry pi to water your plants
# The live implementation of the script is a modified ELC My First Talking Ted
#
# Start by importing the libraries we want to use

import RPi.GPIO as GPIO # This is the GPIO library we need to use the GPIO pins on the Raspberry Pi
import smtplib # This is the SMTP library we need to send the email notification
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
                  smtp_username,
                  smtp_password,
                  smtp_host,
                  smtp_port,
                  smtp_sender,
                  smtp_receivers,
                  message_dead,
                  message_alive
                  )

# Define some variables to be used later on in our script
logfile = 'gardenerbear_log.txt' # Define the location of the logfile
tweetsdb = 'tweets.txt' # Define the location of the tweets file
# Do we want emails or tweets, do we want log messages printed on screen
email_bot_active = 0 # 0 is inactive, 1 active
twitter_bot_active = 1 # 0 is inactive, 1 active
camera_active = 1 # 0 is inactive, 1 active
verbose = 1 # 0 is inactive, 1 active

# How often to check the soil moisture when it's dry (the water is on)
dry_poll = 15 # seconds

# How often to check the soil moisture when it's wet (the water is off)
wet_poll = 15*60 # seconds

# Define the GPIO pin that we have our digital output from our sensor connected to
channel_digital = 17

# Define the GPIO pin that we have our power output from our sensor connected to
channel_power = 18

# Define the GPIO pins that we have our relay module connected to
channel_relayin1 = 14
channel_relayin2 = 15

# Our dummy variables
water = 0
email_warning_wet_sent = 0
email_warning_dry_sent = 0

def writelog(message):
    # This function writes to a logfile, and if verbose is true, it will also print the message to the screen
    messagetolog = "%s, %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(message))
    if verbose:print(messagetolog) # Check to see if we are in verbose mode, if so, print the message to the screen
    with open(logfile, "a+") as file: # Open the logfile for writing in append mode
        file.write(messagetolog) # Write the message to the file

# This is our sendEmail function
def sendEmail(smtp_message):
    try:
        smtpObj = smtplib.SMTP(smtp_host, smtp_port)
        smtpObj.starttls() # If you don't need TLS for your smtp provider, simply remove this line
        smtpObj.login(smtp_username, smtp_password) # If you don't need to login to your smtp provider, simply remove this line
        smtpObj.sendmail(smtp_sender, smtp_receivers, smtp_message)
        log_message = "Successfully sent email"
        writelog(log_message)
    except smtplib.SMTPException:
        log_message = "Error: unable to send email"
        writelog(log_message)
# This is our Twitter streamer class
class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            log_message = "%s tweeted %s at %s" % (data['user']['screen_name'].encode('utf-8'), data['text'].encode('utf-8'), datetime.now().isoformat())
            writelog(log_message)
            # code to water plant
            sensorcheck(user_tweeted = data['user']['screen_name'].encode('utf-8'))
    # Want to disconnect after the first result?
    #self.disconnect()
    def on_error(self, status_code, data):
        log_message = status_code, data
        writelog(log_message)
        GPIO.cleanup()
# This is our Twitter checking function
def twittercheck():
    # Login to the Twitter api
    if twitter_bot_active:
        api = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
        stream = MyStreamer(consumer_key, consumer_secret, access_token, access_token_secret)
        # Get the stream
        log_message = "Tracking Twitter"
        writelog(log_message)
        stream.statuses.filter(track=['@gardenerbear'])
    else:
        log_message = "Twitter is off, ignoring"
        writelog(log_message)
        sensorcheck(gardenerbear)
        if water_status == 'wet':
            log_message = "%s Sleeping %s seconds" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), wet_poll)
            writelog(log_message)
            sleep(wet_poll)
        if water_status == 'dry':
            log_message = "%s Sleeping %s seconds" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), dry_poll)
            writelog(log_message)
            sleep(dry_poll)
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
            message = "Dear @%s, %s BTW, I'm watering the plants! My CPU temp is %sºC" % (user_tweeted, tweetsList[randomChoice].rstrip('\n'), cputemp)
            log_message = "Tweeted %s" % message
            writelog(log_message)
        elif water_status == 'wet':
            message = "Dear @%s, %s BTW, plants don't need water. My CPU temp is %sºC" % (user_tweeted, tweetsList[randomChoice].rstrip('\n'), cputemp)
            sys.stdout.write("{} {}\n".format(len(message), message))
            log_message = "Tweeted %s" % message
            writelog(log_message)
        if camera_active:
            log_message = "Starting Camera"
            writelog(log_message)
            camera = PiCamera()
            log_message = "Camera Started"
            writelog(log_message)
            timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
            photo_path = 'photos/%s.jpg' % timestamp
            log_message = "Taking Picture"
            writelog(log_message)
            camera.capture(photo_path)
            time.sleep(3)
            camera.close()
            log_message = "Closed Camera"
            writelog(log_message)
            with open(photo_path, 'rb') as photo:
                response = api.upload_media(media=photo)
                api.update_status(media_ids=[response['media_id']], status=message)
                log_message = "Tweet Success"
                writelog(log_message)
        else:
            api.update_status(status=message)
            log_message = "Tweet Success"
            writelog(log_message)
        return None
    except IOError:
        if camera_active: camera.close()
        return None

# sensor check function
def sensorcheck(user_tweeted):
    # code to check sensor
    global water, email_warning_wet_sent, email_warning_dry_sent, water_status
    log_message = "Checking Soil Hygrometer"
    writelog(log_message)
    # Set our GPIO numbering to BCM
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO pin to an output
    GPIO.setup(channel_power, GPIO.OUT)
    # Set the GPIO pin to an input
    GPIO.setup(channel_digital, GPIO.IN)
    GPIO.output(channel_power, GPIO.HIGH)  # power the sensor
    time.sleep(1) # Wait for digital sensor to settle - calibrate your potentiometer, make sure both LEDs light up when in water and only one when dry
    if GPIO.input(channel_digital): # soil is dry if true
        log_message = "Dry"
        writelog(log_message)
        if email_bot_active:
            sendEmail(message_dead) # send email
            log_message = "Sent email that plant is dry"
            writelog(log_message)
            email_warning_dry_sent = 1 # only email once
        if twitter_bot_active:
            randomTweet(user_tweeted, water_status = 'dry')
            if not water:
                log_message = "Turn on the water!"
                writelog(log_message)
                water_the_plants()
                water_status = 'dry'
    else: # soil is moist
        log_message = "Wet"
        writelog(log_message)
        if email_bot_active:
            sendEmail(message_alive) # send email
            log_message = "Sent email that plant is wet"
            writelog(log_message)
            email_warning_wet_sent = 1 # only email once
        if twitter_bot_active:
            randomTweet(user_tweeted, water_status = 'wet')
            water_status = 'wet'
    GPIO.output(channel_power, GPIO.LOW) # turn off sensor power
    return None

# watering function
def water_the_plants():
    global water
    water = 1
    # Set our GPIO numbering to BCM
    GPIO.setmode(GPIO.BCM)
    # Set the GPIO relay pin to an output
    #GPIO.setup(channel_relayin1, GPIO.OUT)
    GPIO.setup(channel_relayin2, GPIO.OUT)
    GPIO.output(channel_relayin2, GPIO.LOW)  # relay in 1 on, should turn on pump - but your relay may need to set HIGH for on
    watering_time = 20
    log_message = "Watering %s seconds" % watering_time
    writelog(log_message)
    time.sleep(watering_time) #  seconds watering
    #GPIO.output(channel_relayin1, GPIO.HIGH)  # relay in 1 on, should turn off pump
    GPIO.output(channel_relayin2, GPIO.HIGH)  # relay in 2 off
    water = 0
    return None
try:
    while True:
        twittercheck()

except KeyboardInterrupt:
    GPIO.cleanup()
    if camera_active: camera.close()
    file.close()
