#!/usr/bin/python
# This is a fork of moisture.py from github.com/modmypi/Moisture-Sensor
# It is combined with water_the_plants.py from github.com/cilynx/raspi
# Modified to use Gmail account
# Start by importing the libraries we want to use

import RPi.GPIO as GPIO # This is the GPIO library we need to use the GPIO pins on the Raspberry Pi
import time # This is the time library, we need this so we can use the sleep function
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import os
import random

# Import all our secret stuff from the auth.py file; you have to change the auth-example.py and save it as auth.py
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
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# Define some variables to be used later on in our script

# Do we want emails or tweets
email_bot_active = 0 # 0 is inactive, 1 active
twitter_bot_active = 1 # 0 is inactive, 1 active

# How often to check the soil moisture when it's dry (the water is on)
dry_poll = 1 # seconds

# How often to check the soil moisture when it's wet (the water is off)
wet_poll = 15*60 # seconds

# Define the GPIO pin that we have our digital output from our sensor connected to
channel_digital = 17

# Define the GPIO pin that we have our power output from our sensor connected to
channel_power = 18

# Define the GPIO pins that we have our relay module connected to
channel_relayin1 = 14
#channel_relayin2 = 15

# Our dummy variables
water = 0
email_warning_wet_sent = 0
email_warning_dry_sent = 0

# This is our sendEmail function
def sendEmail(smtp_message):
	try:
		smtpObj = smtplib.SMTP(smtp_host, smtp_port) 
		smtpObj.starttls() # If you don't need TLS for your smtp provider, simply remove this line
		smtpObj.login(smtp_username, smtp_password) # If you don't need to login to your smtp provider, simply remove this line
		smtpObj.sendmail(smtp_sender, smtp_receivers, smtp_message)         
		print "Successfully sent email"
	except smtplib.SMTPException:
		print "Error: unable to send email"
		
# This is our Twitter streamer class
class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
        #    print "%s tweeted %s at %s" % (data['user']['screen_name'].encode('utf-8'), data['text'].encode('utf-8'), datetime.now().isoformat()) #For debugging only
            if "@gardenerbear" in str.lower(data['text'].encode('utf-8')):
            	if "are you thirsty" in str.lower(data['text'].encode('utf-8')):
					sensorcheck()    
            	if "drink water" in str.lower(data['text'].encode('utf-8')):
            		sensorcheck()
            	# code to water plant 
        # Want to disconnect after the first result?
        #self.disconnect()
    def on_error(self, status_code, data):
        print status_code, data
        GPIO.cleanup()
        
# CPU temp function
def PiCPUtemp():
	cmd = '/opt/vc/bin/vcgencmd measure_temp'
	line = os.popen(cmd).readline().strip()
	temp = line.split('=')[1].split("'")[0]
	return temp

# Random tweeting function
def randomTweet(user_tweeted, water_status):
    try:
        tweetsFile = open(os.path.join(__location__,'tweets.txt'),'r')
        tweetsList = tweetsFile.readlines()
        tweetsFile.close()
        randomChoice = random.randrange(len(tweetsList))
        cputemp = PiCPUtemp()
        #print (tweetsList[randomChoice]) #For debugging only
        #print cputemp #For debugging only
        if water_status == 'dry':
        	message = "@%s, %s need watering and my CPU temperature is %s" % (user_tweeted, tweetsList[randomChoice], cputemp)
        elif water_status == 'wet':
        	message = "@%s, %s don't need watering and my CPU temperature is %s" % (user_tweeted, tweetsList[randomChoice], cputemp)
        timestamp = datetime.now().isoformat()
    	photo_path = '/home/pi/Moisture-Sensor/photos/%s.jpg' % timestamp
    	camera.capture(photo_path)
    	time.sleep(3)
    	with open(photo_path, 'rb') as photo:
    		response = api.upload_media(media=photo)
    		api.update_status_with_media(media_ids=[response['media_id']], status=message)
        return None
    except IOError:
        return None 
# sensor check and water function
def sensorcheck():
# code to check sensor
	GPIO.output(channel_power, GPIO.HIGH)  # power the sensor
	time.sleep(1) # Wait for digital sensor to settle - calibrate your potentiometer, make sure both LEDs light up when in water and only one when dry
	if GPIO.input(channel_digital): # soil is dry if true
			print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Dry"))
			if email_bot_active:
				sendEmail(message_dead) # send email
				email_warning_dry_sent = 1 # only email once
			if twitter_bot_active:
				randomTweet(user_tweeted = data['user']['screen_name'].encode('utf-8'), water_status = 'dry')
			if not water:
				print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Turn on the water!"))
				GPIO.output(channel_relayin1, GPIO.HIGH)  # relay in 1 on, should turn on pump
				time.sleep(10) # 10 seconds watering
				GPIO.output(channel_relayin1, GPIO.LOW)  # relay in 1 on, should turn off pump
				water = 1
	else: # soil is moist
			print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Wet"))
			if email_bot_active:
				sendEmail(message_alive) # send email
				email_warning_wet_sent = 1 # only email once
			if twitter_bot_active:
				randomTweet(user_tweeted = data['user']['screen_name'].encode('utf-8'), water_status = 'wet')
			if water:
				print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Turn off the water!"))  # this part of the script must be expanded to power off the relay
				water = 0
	GPIO.output(channel_power, GPIO.LOW) # turn off sensor power
	if water:
			time.sleep(dry_poll)
			if email_bot_active:
				email_warning_wet_sent = 0 # 
	else:
			time.sleep(wet_poll)
			if email_bot_active:
				email_warning_dry_sent = 0 
# initialize our camera (idea from Tweeting Babbage)
camera = PiCamera()		          
# Set our GPIO numbering to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin to an input
GPIO.setup(channel_digital, GPIO.IN)

# Set the GPIO pin to an output
GPIO.setup(channel_power, GPIO.OUT)
GPIO.setup(channel_relayin1, GPIO.OUT)
#GPIO.setup(channel_relayin2, GPIO.OUT)

GPIO.output(channel_relayin1, GPIO.LOW)  # relay in 1 off
#GPIO.output(channel_relayin2, GPIO.LOW)  # relay in 2 off

# This is an infinite loop to keep our script running
try:
    while True:
        # Login to the Twitter api
        if twitter_bot_active:
	    api = Twython(consumer_key, consumer_secret, access_token, access_token_secret) 
	    stream = MyStreamer(consumer_key, consumer_secret, access_token, access_token_secret)
	    stream.statuses.filter(track=['drink water','are you thirsty'])
        GPIO.output(channel_power, GPIO.HIGH)  # power the sensor
        time.sleep(1) # Wait for digital sensor to settle - calibrate your potentiometer, make sure both LEDs light up when in water and only one when dry
        if GPIO.input(channel_digital): # soil is dry if true
            print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Dry"))
            if email_bot_active:
            	sendEmail(message_dead) # send email
            	email_warning_dry_sent = 1 # only email once
            if twitter_bot_active:
            	randomTweet(user_tweeted = data['user']['screen_name'].encode('utf-8'), water_status = 'dry')
            if not water:
                print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Turn on the water!"))
                GPIO.output(channel_relayin1, GPIO.HIGH)  # relay in 1 on, should turn on pump
                time.sleep(10) # 10 seconds watering
                GPIO.output(channel_relayin1, GPIO.LOW)  # relay in 1 on, should turn off pump
                water = 1
        else: # soil is moist
            print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Wet"))
            if email_bot_active:
            	sendEmail(message_alive) # send email
            	email_warning_wet_sent = 1 # only email once
            if twitter_bot_active:
            	randomTweet(user_tweeted = data['user']['screen_name'].encode('utf-8'), water_status = 'wet')
            if water:
                print ','.join((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Turn off the water!"))  # this part of the script must be expanded to power off the relay
                water = 0
        GPIO.output(channel_power, GPIO.LOW) # turn off sensor power
        if water:
            time.sleep(dry_poll)
            if email_bot_active:
            	email_warning_wet_sent = 0 # 
        else:
            time.sleep(wet_poll)
            if email_bot_active:
            	email_warning_dry_sent = 0 
except KeyboardInterrupt:
    GPIO.cleanup()
    camera.close() # ensures a clean camera exit
finally:
	GPIO.cleanup() # ensures a clean exit
    camera.close() # ensures a clean camera exit