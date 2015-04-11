#!/bin/bash

echo "Starting GPSD...."
sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
echo "Done... Sleeping for 5 seconds"
sleep 1
echo "1"
sleep 1
echo "2"
sleep 1
echo "3"
sleep 1
echo "4"
sleep 1
echo "5"
echo "Starting main logging script"
sudo python /home/pi/pidashcam/main.py
