#!/bin/bash

sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
sleep 10
sudo python main.py
