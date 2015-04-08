import RPi.GPIO as GPIO
import time


def restart():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    input_state = GPIO.input(16)
    if input_state == False:
        restart()
