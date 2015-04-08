import gps

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
    try:
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
	#print report
        if report['class'] == 'TPV':
            report.time = str(report.time)
            report.device = str(report.device)
            report.lon = str(report.lon)
            report.lat = str(report.lat)
            report.mode = str(report.mode)
            report.eps = str(report.eps)
            report.epx = str(report.epx)
            report.epy = str(report.epy)
            report.epv = str(report.epv)
            report.speed = str(report.speed)
            tosave = report.time + "," + report.device + "," + report.lon + "," + report.lat + "," + report.mode + "," + report.eps + "," + report.epx + "," + report.epy + "," + report.epv + "," + report.speed + "\n"
            f = open('test.txt', 'a') #create a file using the given input
            f.write(tosave)
            f.close()
            #
            #if hasattr(report, 'time'):
            #    print report.time
            #if hasattr(report, 'device'):
            #    print report.device
            #if hasattr(report, 'lon'):
            #    print report.lon
        #   if hasattr(report, 'lat'):
        #        print report.lat
        #    if hasattr(report, 'mode'):
        #        print report.mode
        #    if hasattr(report, 'eps'):
        #        print report.eps
        #    if hasattr(report, 'epx'):
        #        print report.epx
        #    if hasattr(report, 'epy'):
        #        print report.epy
        #    if hasattr(report, 'epv'):
        #        print report.epv
        #    if hasattr(report, 'speed'):
        #        print report.speed
    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"
