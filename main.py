#!/usr/bin/python

import pygame
import sys
import os
import time
import math
import datetime
import gps
import RPi.GPIO as GPIO  # Import GPIO library
from pygame.locals import *
from time import strftime, gmtime, sleep
from smbus import SMBus
from ctypes import c_short
from LSM9DS0 import *


GPIO.setmode(GPIO.BOARD)  # Use board pin numbering
GPIO.setup(13, GPIO.OUT)  # Setup GPIO Pin 7 to OUT


logfilename = "/home/pi/pidashcam/logs/" + time.strftime("%Y%m%d-%H%M%S")
#bus = smbus.SMBus(1)
bus = SMBus(1)         # 0 for R-Pi Rev. 1, 1 for Rev. 2

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
# [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
G_GAIN = 0.070
# Loop period = 41ms.   This needs to match the time it takes each loop to run
LP = 0.040
AA = 0.90      # Complementary filter constant


def writeACC(register, value):
    bus.write_byte_data(ACC_ADDRESS, register, value)
    return -1


def writeMAG(register, value):
    bus.write_byte_data(MAG_ADDRESS, register, value)
    return -1


def writeGRY(register, value):
    bus.write_byte_data(GYR_ADDRESS, register, value)
    return -1


def readACCx():
    acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
    acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
    acc_combined = (acc_l | acc_h << 8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCy():
    acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
    acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
    acc_combined = (acc_l | acc_h << 8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCz():
    acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
    acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
    acc_combined = (acc_l | acc_h << 8)

    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readMAGx():
    mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_X_L_M)
    mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_X_H_M)
    mag_combined = (mag_l | mag_h << 8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536


def readMAGy():
    mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Y_L_M)
    mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Y_H_M)
    mag_combined = (mag_l | mag_h << 8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536


def readMAGz():
    mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Z_L_M)
    mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Z_H_M)
    mag_combined = (mag_l | mag_h << 8)

    return mag_combined if mag_combined < 32768 else mag_combined - 65536


def readGYRx():
    gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_X_L_G)
    gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_X_H_G)
    gyr_combined = (gyr_l | gyr_h << 8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


def readGYRy():
    gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Y_L_G)
    gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Y_H_G)
    gyr_combined = (gyr_l | gyr_h << 8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


def readGYRz():
    gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Z_L_G)
    gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Z_H_G)
    gyr_combined = (gyr_l | gyr_h << 8)

    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


# initialise the accelerometer
# z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG1_XM, 0b01100111)
writeACC(CTRL_REG2_XM, 0b00100000)  # +/- 16G full scale

# initialise the magnetometer
writeMAG(CTRL_REG5_XM, 0b11110000)  # Temp enable, M data rate = 50Hz
writeMAG(CTRL_REG6_XM, 0b01100000)  # +/-12gauss
writeMAG(CTRL_REG7_XM, 0b00000000)  # Continuous-conversion mode

# initialise the gyroscope
writeGRY(CTRL_REG1_G, 0b00001111)  # Normal power mode, all axes enabled
writeGRY(CTRL_REG4_G, 0b00110000)  # Continuos update, 2000 dps full scale

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0

os.environ["SDL_FBDEV"] = "/dev/fb1"


pygame.init()

# set up the window
screen = pygame.display.set_mode((128, 160), 0, 32)

pygame.display.set_caption('Drawing')
pygame.mouse.set_visible(0)

# set up the colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)
GREEN = (0, 255,   0)
BLUE = (0,   0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255,   0, 255)
YELLOW = (255, 255,   0)

# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(WHITE)
box = pygame.draw.rect(background, BLACK, (0, 0, 128, 160))
# colour (starx, staryy, width, height

speed = 0
displayspeed = 0
running = True
# run the game loop
while running:
    report = session.next()
    if report['class'] == 'TPV':
        if hasattr(report, 'time'):
            report.time = str(report.time)
        else:
            report.time = str("ERROR 1")
        if hasattr(report, 'device'):
            report.device = str(report.device)
        else:
            report.device = str("ERROR 1")
        if hasattr(report, 'lon'):
            report.lon = str(report.lon)
        else:
            report.lon = str("ERROR 1")
        if hasattr(report, 'lat'):
            report.lat = str(report.lat)
        else:
            report.lat = str("ERROR 1")
        if hasattr(report, 'mode'):
            report.mode = str(report.mode)
        else:
            report.mode = str("ERROR 1")
        if hasattr(report, 'eps'):
            report.eps = str(report.eps)
        else:
            report.eps = str("ERROR 1")
        if hasattr(report, 'epx'):
            report.epx = str(report.epx)
        else:
            report.epx = str("ERROR 1")
        if hasattr(report, 'epy'):
            report.epy = str(report.epy)
        else:
            report.epy = str("ERROR 1")
        if hasattr(report, 'epv'):
            report.epv = str(report.epv)
        else:
            report.epv = str("ERROR 1")
        if hasattr(report, 'speed'):
            report.speed = 2.23693629 * report.speed
            report.speed = "{:.0f}".format(report.speed)
            report.speed = str(report.speed)
        else:
            report.speed = str("ERROR 1")
    else:
        report.time = str("ERROR 2")
        report.device = str("ERROR 2")
        report.lon = str("ERROR 2")
        report.lat = str("ERROR 2")
        report.mode = str("ERROR 2")
        report.eps = str("ERROR 2")
        report.epx = str("ERROR 2")
        report.epy = str("ERROR 2")
        report.epv = str("ERROR 2")
        report.speed = str("ERROR 2")
    speed = speed + 1
    background.fill(BLACK)
    # Display some text
    font = pygame.font.Font("/home/pi/pidashcam/bold.ttf", 72)
    displayspeed = report.speed
    text = font.render(displayspeed, 1, (WHITE))
    textpos = text.get_rect(centerx=background.get_width() / 2, centery=26)
    background.blit(text, textpos)

    font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 14)
    text = font.render("MPH", 1, (WHITE))
    textpos = text.get_rect(centerx=background.get_width() / 2, centery=65)
    background.blit(text, textpos)

    font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 14)
    currenttime = time.strftime("%H:%M:%S", gmtime())
    gmttext = " GMT"
    currenttime = currenttime + gmttext
    text = font.render(currenttime, 1, (WHITE))
    textpos = text.get_rect(centerx=background.get_width() / 2, centery=80)
    background.blit(text, textpos)
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
    font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 12)
    tempprint = "Temp:" + str(t) + "C"
    temptext = font.render(tempprint, 1, (WHITE))
    presprint = "Pres:" + str(p) + "hPa"
    prestext = font.render(presprint, 1, (WHITE))
    #textpos = text.get_rect(centerx=60,centery=90)
    #background.blit(text, textpos)
    screen.blit(temptext, (5, 90))
    screen.blit(prestext, (5, 102))
    pygame.display.flip()
    screen.blit(background, (0, 0))

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
    font = pygame.font.Font("/home/pi/pidashcam/audi.ttf", 12)
    textaccx = font.render("AX:" + str(textaccxhelper), 1, (WHITE))
    textaccy = font.render("AY:" + str(textaccyhelper), 1, (WHITE))
    textcfax = font.render("CX:" + str(textcfaxhelper), 1, (WHITE))
    textcfay = font.render("CY:" + str(textcfayhelper), 1, (WHITE))
    texthead = font.render("HD:" + str(textheadhelper), 1, (WHITE))

    screen.blit(textaccx, (5, 114))
    screen.blit(textaccy, (5, 128))
    screen.blit(textcfax, (70, 114))
    screen.blit(textcfay, (70, 128))
    screen.blit(texthead, (5, 142))
    background.blit(text, textpos)

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
    tosave = report.time + "," + report.device + "," + report.lon + "," + report.lat + "," + report.mode + "," + report.eps + "," + report.epx + "," + report.epy + "," + report.epv + \
        "," + report.speed + "," + textaccxsave + "," + textaccysave + "," + textcfaxsave + "," + \
        textcfaysave + "," + textheadsave + "," + \
        str(t) + "," + str(p) + "," + currenttime + "\n"
    # create a file using the given input
    f = open(logfilename + '.nickgps', 'a')
    f.write(tosave)
    f.close()
    GPIO.output(13, False)  # Turn on GPIO pin 7
