import RPi.GPIO as GPIO
import time
import os

def Int_shutdown(channel):
	# shutdown our Raspberry Pi
	os.system("sudo shutdown -h now")

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(16, GPIO.FALLING, callback = Int_shutdown, bouncetime = 2000)

while 1:
        time.sleep(1)
