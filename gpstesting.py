from gps import *
import time
import threading
import math

class GpsController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:
            # grab EACH set of gpsd info to clear the buffer
            self.gpsd.next()

    def stopController(self):
        self.running = False
  
    @property
    def fix(self):
        return self.gpsd.fix

    @property
    def utc(self):
        return self.gpsd.utc

    @property
    def satellites(self):
        return self.gpsd.satellites

if __name__ == '__main__':
    # create the controller
    gpsc = GpsController() 
    try:
        # start controller
        gpsc.start()
        while True:
            lat = "lat:", gpsc.fix.latitude
	    long = "longitude ", gpsc.fix.longitude
            time = "time utc ", gpsc.utc, " + ", gpsc.fix.time
            alt = "altitude (m)", gpsc.fix.altitude
            eps = "eps ", gpsc.fix.eps
            epx = "epx ", gpsc.fix.epx
            epv = "epv ", gpsc.fix.epv
            ept = "ept ", gpsc.gpsd.fix.ept
            speed = "speed (m/s) ", gpsc.fix.speed
            climb = "climb ", gpsc.fix.climb
            track = "track ", gpsc.fix.track
            mode = "mode ", gpsc.fix.mode
            sats = "sats ", gpsc.satellites
            print lat + "," + long + "," + time + "," + alt + "," + eps + "," + epx + "," + epv + "," + ept + "," + speed + "," + climb + "," + track + "," + mode + "," + sats
	    time.sleep(0.5)

    finally:
        print "Stopping gps controller"
        gpsc.stopController()
        #wait for the tread to finish
        gpsc.join()
      
    print "Done"
