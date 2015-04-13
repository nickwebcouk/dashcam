import RPi.GPIO as GPIO
import time
import os

def restart():
    command = "/usr/bin/sudo /sbin/halt"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(16, GPIO.FALLING, callback = Int_shutdown, bouncetime = 2000)

while 1:
        time.sleep(1)
