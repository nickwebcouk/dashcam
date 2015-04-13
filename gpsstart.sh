#!/bin/bash

echo "Starting GPSD...."
sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
echo "Starting shutdown monitor..."
sudo python /home/pi/pidashcam/shutdown.py &
echo "Starting main logging script"
sudo python /home/pi/pidashcam/main.py &
