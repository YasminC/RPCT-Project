import tweepy 
from omxplayer import OMXPlayer
from time import sleep
from PIL import Image
from picamera import PiCamera
from gpiozero import Button
from gpiozero import MotionSensor
from subprocess import call  
from datetime import datetime  
import sys
import os

leftbutton = Button(21)
rightbutton = Button(16)
pir = MotionSensor(4)

#add your twitter app stuff
consumer_key = ''  
consumer_secret = ''  
access_token = ''  
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  
auth.set_access_token(access_token, access_token_secret)  

api = tweepy.API(auth) 

tweet_text = "Terror can be anyone. Anywhere. So beware..."

#function runs when 'dare' button pressed
def terrorcam():
    print("running terrorcam")
    #display a basic camera preview
    with PiCamera() as camera:
        camera.resolution = (1280, 720)
        camera.framerate = 24
        camera.start_preview()
        #overlay text to camera preview
        camera.annotate_text = "Terror is watching"
        #overlay image to the camera preview
        img = Image.open('pov.jpg')

        pad = Image.new('RGB', (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
            ))

        pad.paste(img, (0, 0))

        o = camera.add_overlay(pad.tostring(), size=img.size)

        o.alpha = 128
        o.layer = 3
        #playing omxplayer soundfile from console, wasn't working through python with wav for some reason
        call(['omxplayer -o local breath.wav'], shell=True)
        sleep(1)
        camera.stop_preview()
        
    #play the video from where it was paused
    player.play()
    print("player is played after terrorcam")

def photo_tweet(photo_path):
    i = datetime.now()
    tweettime = i.strftime('%Y/%m/%d %H:%M:%S')
    status = tweet_text + ' #WhoIsTerror ' + tweettime   
  
    # Add text overlay of data on the photo we just took  
    print "about to set overlay_text variable"  
    overlay_text = "/usr/bin/convert "+ photo_path + "  -pointsize 36 -fill white -annotate +40+728 '" + tweettime + "' "  
    overlay_text += " -pointsize 36 -fill white -annotate +550+60 'I am Terror ' " + photo_path  
  
    print "overlaying text"  
    call ([overlay_text], shell=True)  
  
    print "adding your logo" # you'll need a file called overlay.png in /home/pi  
    overlay_text = '/usr/bin/convert '+ photo_path + ' /home/pi/twitteroverlay.png -gravity center -composite ' + photo_path  
    call ([overlay_text], shell=True)  
    print "added logo 1"  
  
    print "tweeting photo " + photo_path 
    api.update_with_media(photo_path, status=status)      
    print "photo tweeted, deleting .jpg"  
    cmd = 'rm ' + photo_path   
    call ([cmd], shell=True)

def tweetpic():
    print("detected")
    rightbutton.when_pressed = None
    
    #display preview image with text telling user to press right button if they want it sent to twitter
    i = datetime.now()  
    now = i.strftime('%Y%m%d-%H%M%S')
    photo_path = '/home/pi/' + now + '.jpg'
    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        camera.annotate_text = "Press red button to post to Twitter"
        rightbutton.wait_for_press()
        camera.annotate_text = ""
        camera.capture(photo_path)
        camera.stop_preview()
        
    photo_tweet(photo_path)

    sleep(5)
        
while True:
    #replace with you video, always needs to reestablish variable or won't loop video
    player = OMXPlayer("test.mov")
    print("Press the left button to play")
    rightbutton.when_pressed = player.pause
    leftbutton.wait_for_press()
    player.play()
    print(player.playback_status())
    try:
        while player.playback_status():
            if player.playback_status() == "Paused":
                terrorcam()
    except:
        pass
    print("Waiting for motion")
    pir.wait_for_motion()
    tweetpic()
    
            
