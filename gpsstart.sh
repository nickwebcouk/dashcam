#!/bin/bash

sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
sudo python gps.py
