#!/usr/bin/python
# These are the twitter variables for your app, need to modify this file to run on your raspberry pi
consumer_key = 'your twitter consumer key here'
consumer_secret = 'your twitter consumer secret key here'
access_token = 'your twitter access token here'
access_token_secret = 'your twitter secret access token here'

# You might not need the username and password variable, depends if you are using a provider or if you have your raspberry pi setup to send emails
# If you have setup your raspberry pi to send emails, then you will probably want to use 'localhost' for your smtp_host (this is generally a bad idea as your email may end up in spam)

smtp_username = "enter_username_here" # This is the username used to login to your SMTP provider
smtp_password = "enter_password_here" # This is the password used to login to your SMTP provider
smtp_host = "smtp.gmail.com" # This is the host of the SMTP provider
smtp_port = 587 # This is the port that your SMTP provider uses

smtp_sender = "sender@email.com" # This is the FROM email address
smtp_receivers = ['receiver@email.com'] # This is the TO email address

# The next two variables use triple quotes, these allow us to preserve the line breaks in the string.

# This is the message that will be sent when NO moisture is detected

message_dead = """From: Sender Name <sender@email.com>
To: Receiver Name <receiver@email.com>
Subject: Moisture Sensor Notification

Warning, no moisture detected! Plant death imminent!!! :'(
"""

# This is the message that will be sent when moisture IS detected again

message_alive = """From: Sender Name <sender@email.com>
To: Receiver Name <receiver@email.com>
Subject: Moisture Sensor Notification

Panic over! Plant has water again :)
"""
