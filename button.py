import RPi.GPIO as GPIO
import time


def restart():
    command = "/usr/bin/sudo /sbin/halt"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


GPIO.setmode(GPIO.BOARD)

GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    input_state = GPIO.input(13)
    if input_state == False:
        restart()
