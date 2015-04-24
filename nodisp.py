#!/usr/bin/python

# TODO
# 1) Remove extra code to a seperate file
# 2) Time loop to assist with BMP180 readings
# 3) Fix variable names, add in string creating sections ONLY before writing to file/screen
# 3) Add in pygame code to get screen update again
# 3) Hook up GPS to Windows to check baud speed and transmission rates etc



import pygame
import sys
import os
from gps import *
from time import *
import time
import math
import datetime
import RPi.GPIO as GPIO  # Import GPIO library
from pygame.locals import *
from time import strftime, gmtime, sleep
from smbus import SMBus
from ctypes import c_short
from LSM9DS0 import *
import threading


def include(filename):
    if os.path.exists(filename):
        execfile(filename)


include('pidashinc.py')


GPIO.setmode(GPIO.BOARD)  # Use board pin numbering
GPIO.setup(13, GPIO.OUT)  # Setup GPIO Pin 7 to OUT


logfilename = "/home/pi/pidashcam/logs/" + time.strftime("%Y%m%d-%H%M%S")
#bus = smbus.SMBus(1)
bus = SMBus(1)         # 0 for R-Pi Rev. 1, 1 for Rev. 2

gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)



os.environ["SDL_FBDEV"] = "/dev/fb1"

speed = 0
displayspeed = 0

savedatatime = "None"
savedatadevice = "None"
savedatalon = "None"
savedatalat = "None"
savedatamode = "None"
savedataeps = "None"
savedataepx = "None"
savedataepy = "None"
savedataepv = "None"
savedataspeed = "None"
textaccxsave = "None"
textaccysave = "None"
textcfaxsave = "None"
textcfaysave = "None"
textheadsave = "None"
currenttime = "None"
savedataclimb = "None"
savedatatrack = "None"
savedatamode = "None"
savedatasats = "None"



#import pdb; pdb.set_trace()
class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps("localhost", "2947")
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
          gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
    gpsp = GpsPoller() # create the thread
    try:
        gpsp.start() # start it up

        while True:
            savedatadevice = "Unknown"
            savedatalat = gpsd.fix.latitude
            savedatalon = gpsd.fix.longitude
            savedatatimeutc = gpsd.utc
            savedatatimefix = gpsd.fix.time
            savedataaltitude  = gpsd.fix.altitude
            savedataeps = gpsd.fix.eps
            savedataepx = gpsd.fix.epx
            savedataepy = gpsd.fix.epv
            savedataepv = gpsd.fix.ept
            savedataspeed = gpsd.fix.speed
            savedataclimb = gpsd.fix.climb
            savedatatrack = gpsd.fix.track
            savedatamode = gpsd.fix.mode
            savedatasats = gpsd.satellites
            savedatasats = len(savedatasats)
            speed = speed + 1
            #background.fill(BLACK)
            # Display some text
            #font = pygame.font.Font("/home/pi/pidashcam/bold.ttf", 72)
            #displayspeed = savedataspeed
            #text = font.render(displayspeed, 1, (WHITE))
            #textpos = text.get_rect(centerx=background.get_width() / 2, centery=26)
            #background.blit(text, textpos)

            #font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 14)
            #text = font.render("MPH", 1, (WHITE))
            #textpos = text.get_rect(centerx=background.get_width() / 2, centery=65)
            #background.blit(text, textpos)

            #font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 14)
            currenttime = time.strftime("%H:%M:%S", gmtime())
            gmttext = " GMT"
            currenttime = currenttime + gmttext
            #text = font.render(currenttime, 1, (WHITE))
            #textpos = text.get_rect(centerx=background.get_width() / 2, centery=80)
            #background.blit(text, textpos)
        # Start Temp and pressure monitor part...
        # put into function!!!
        # Pressure and Temprature
            addr = 0x77
            oversampling = 3        # 0..3

            # return two bytes from data as a signed 16-bit value
            def get_short(data, index):
                return c_short((data[index] << 8) + data[index + 1]).value

            # return two bytes from data as an unsigned 16-bit value
            def get_ushort(data, index):
                return (data[index] << 8) + data[index + 1]
            (chip_id, version) = bus.read_i2c_block_data(addr, 0xD0, 2)
            # print "Chip Id:", chip_id, "Version:", version
            # print
            # print "Reading calibration data..."
            # Read whole calibration EEPROM data
            cal = bus.read_i2c_block_data(addr, 0xAA, 22)
            # Convert byte data to word values
            ac1 = get_short(cal, 0)
            ac2 = get_short(cal, 2)
            ac3 = get_short(cal, 4)
            ac4 = get_ushort(cal, 6)
            ac5 = get_ushort(cal, 8)
            ac6 = get_ushort(cal, 10)
            b1 = get_short(cal, 12)
            b2 = get_short(cal, 14)
            mb = get_short(cal, 16)
            mc = get_short(cal, 18)
            md = get_short(cal, 20)
            # print "Starting temperature conversion..."
            bus.write_byte_data(addr, 0xF4, 0x2E)
            sleep(0.005)
            (msb, lsb) = bus.read_i2c_block_data(addr, 0xF6, 2)
            ut = (msb << 8) + lsb
            # print "Starting pressure conversion..."
            bus.write_byte_data(addr, 0xF4, 0x34 + (oversampling << 6))
            sleep(0.04)
            (msb, lsb, xsb) = bus.read_i2c_block_data(addr, 0xF6, 3)
            up = ((msb << 16) + (lsb << 8) + xsb) >> (8 - oversampling)
            # print "Calculating temperature..."
            x1 = ((ut - ac6) * ac5) >> 15
            x2 = (mc << 11) / (x1 + md)
            b5 = x1 + x2
            t = (b5 + 8) >> 4
            # print "Calculating pressure..."
            b6 = b5 - 4000
            b62 = b6 * b6 >> 12
            x1 = (b2 * b62) >> 11
            x2 = ac2 * b6 >> 11
            x3 = x1 + x2
            b3 = (((ac1 * 4 + x3) << oversampling) + 2) >> 2
            x1 = ac3 * b6 >> 13
            x2 = (b1 * b62) >> 16
            x3 = ((x1 + x2) + 2) >> 2
            b4 = (ac4 * (x3 + 32768)) >> 15
            b7 = (up - b3) * (50000 >> oversampling)
            p = (b7 * 2) / b4
            #p = (b7 / b4) * 2
            x1 = (p >> 8) * (p >> 8)
            x1 = (x1 * 3038) >> 16
            x2 = (-7357 * p) >> 16
            p = p + ((x1 + x2 + 3791) >> 4)
            # print
            t = t / 10.0
            p = p / 100.0
            #font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 12)
            tempprint = "Temp:" + str(t) + "C"
            #temptext = font.render(tempprint, 1, (WHITE))
            presprint = "Pres:" + str(p) + "hPa"
            #prestext = font.render(presprint, 1, (WHITE))
            #textpos = text.get_rect(centerx=60,centery=90)
            #background.blit(text, textpos)
            #screen.blit(temptext, (5, 90))
            #screen.blit(prestext, (5, 102))
            #pygame.display.flip()
            #screen.blit(background, (0, 0))

            # Headings and other stuff

            AccXangle = (math.atan2(readACCy(), readACCz()) + M_PI) * RAD_TO_DEG
            AccYangle = (math.atan2(readACCz(), readACCx()) + M_PI) * RAD_TO_DEG
            # Convert Gyro raw to degrees per second
            rate_gyr_x = readGYRx() * G_GAIN
            rate_gyr_y = readGYRy() * G_GAIN
            rate_gyr_z = readGYRz() * G_GAIN
            # Calculate the angles from the gyro. LP = loop period
            gyroXangle += rate_gyr_x * LP
            gyroYangle += rate_gyr_y * LP
            gyroZangle += rate_gyr_z * LP
            # Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up.
            # Two different pieces of code are used depending on how your IMU is mounted.
            # If IMU is upside down
            #
            # if AccXangle >180:
            #        AccXangle -= 360.0
            # AccYangle-=90
            # if (AccYangle >180):
            #        AccYangle -= 360.0
            #//If IMU is up the correct way, use these lines
            AccXangle -= 180.0
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0
            # Complementary filter used to combine the accelerometer and gyro values.
            CFangleX = AA * (CFangleX + rate_gyr_x * LP) + (1 - AA) * AccXangle
            CFangleY = AA * (CFangleY + rate_gyr_y * LP) + (1 - AA) * AccYangle
            heading = 180 * math.atan2(readMAGy(), readMAGx()) / M_PI
            if heading < 0:
                heading += 360

            textaccxhelper = "{:.2f}".format(AccXangle)
            textaccyhelper = "{:.2f}".format(AccYangle)
            textcfaxhelper = "{:.2f}".format(CFangleX)
            textcfayhelper = "{:.2f}".format(CFangleY)
            textheadhelper = "{:.0f}".format(heading)
            # font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 12)
            #textaccx = font.render("AX:" + str(textaccxhelper), 1, (WHITE))
            #textaccy = font.render("AY:" + str(textaccyhelper), 1, (WHITE))
            #textcfax = font.render("CX:" + str(textcfaxhelper), 1, (WHITE))
            #textcfay = font.render("CY:" + str(textcfayhelper), 1, (WHITE))
            #texthead = font.render("HD:" + str(textheadhelper), 1, (WHITE))

            #screen.blit(textaccx, (5, 114))
            #screen.blit(textaccy, (5, 128))
            #screen.blit(textcfax, (70, 114))
            #screen.blit(textcfay, (70, 128))
            #screen.blit(texthead, (5, 142))
            #background.blit(text, textpos)

            textaccxsave = textaccxhelper
            textaccysave = textaccyhelper
            textcfaxsave = textcfaxhelper
            textcfaysave = textcfayhelper
            textheadsave = textheadhelper
            GPIO.output(13, True)  # Turn on GPIO pin 7
            # GPS TIME            GPS DEVICE            LONGTITUDE         LATITUDE
            # REPORT MODE
            # GPS SPEED            GYRO ACC X           GYRO ACC Y           GYRO K X
            # GYRO K Y             GYRO HEAD            TEMP           PRESS
            # DEVICE TIME
            savedatatime = str(savedatatime)
            savedatadevice = str(savedatadevice)
            savedatalon = str(savedatalon)
            savedatalat = str(savedatalat)
            savedatamode = str(savedatamode)
            savedataeps = str(savedataeps)
            savedataepx = str(savedataepx)
            savedataepy = str(savedataepy)
            savedataepv = str(savedataepv)
            savedataspeed = str(savedataspeed)
            textaccxsave = str(textaccxsave)
            textaccysave = str(textaccysave)
            textcfaxsave = str(textcfaxsave)
            textcfaysave = str(textcfaysave)
            textheadsave = str(textheadsave)
            currenttime = str(currenttime)
            savedataclimb = str(savedataclimb)
            savedatatrack = str(savedatatrack)
            savedatamode = str(savedatamode)
            savedatasats = str(savedatasats)

            tosave = savedatatime + "," + savedatadevice + "," + savedatalon + "," + savedatalat + "," + savedatamode + "," + savedataeps + "," + savedataepx + "," + savedataepy + "," + savedataepv + "," + savedataspeed + "," + textaccxsave + "," + textaccysave + "," + textcfaxsave + "," + textcfaysave + "," + textheadsave + "," + str(t) + "," + str(p) + "," + currenttime + "," + savedataclimb + "," + savedatatrack + "," + savedatamode + "," + savedatasats + "\n"
            print tosave
            #create a file using the given input
            f = open(logfilename + '.nickgps', 'a')
            f.write(tosave)
            f.close()
            GPIO.output(13, False)  # Turn on GPIO pin 7

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print "\nKilling Thread..."
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing
        print "Done.\nExiting."
