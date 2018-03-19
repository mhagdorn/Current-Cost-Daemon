from __future__ import with_statement
import serial
import time
from xml.dom import minidom
from optparse import OptionParser
import sys
import daemon,lockfile.pidlockfile

def readCurrentCost(port,interval,outname,baudrate=57600):

    if outname==None:
        outfile = sys.stdout
    else:
        outfile = open(outname,'a',buffering=1)

    #open serial port
    ser = serial.Serial(port=port, baudrate=baudrate,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,timeout=5)

    # get current time
    startTime = time.time()
    # and initialise data
    temp = {}
    power = {}
    count = {}
    
    while True:
        line = ser.readline()
        thisTime = time.time()
        if len(line)>0:
            xmldoc = minidom.parseString(line)
            watts_nodes = {}
            # parse the xml
            try:
                temperature_nodes = xmldoc.getElementsByTagName('tmpr')
                watts_nodes = xmldoc.getElementsByTagName('ch1')[0].getElementsByTagName('watts')
                sensor_nodes = xmldoc.getElementsByTagName('sensor')
            except:
                continue
            sensor = int(sensor_nodes[0].childNodes[0].nodeValue)
            # check if sensor is already recorded
            if sensor not in count.keys():
                count[sensor] = 0
                temp[sensor] = 0.
                power[sensor] = 0.
            # accumulate data
            temp[sensor]  += float(temperature_nodes[0].childNodes[0].nodeValue)
            power[sensor] += float(watts_nodes[0].childNodes[0].nodeValue)
            count[sensor] += 1

            # check if we should write out data
            if thisTime-startTime >= interval:
                done = 0
                have_temp = False
                outfile.write("%s "%(time.strftime("%Y-%m-%d %H:%M:%S",
                                                   time.gmtime(startTime+(thisTime-startTime)/2.))))
                # loop over sensors
                for i in range(0,10):
                    if i in count.keys():
                        if count[i]>0:
                            if not have_temp:
                               outfile.write("%f "%(temp[i]/count[i]))
                               have_temp = True
                            outfile.write("%f "%(power[i]/count[i]))
                            # reset counters
                            count[i] = 0
                            temp[i] = 0.
                            power[i] = 0.
                            done+=1
                    else:
                        outfile.write('NaN ')
                    # check we have handled all the data
                    if len(count.keys()) == done:
                        break
                outfile.write('\n')
                startTime = thisTime

if __name__ == "__main__":
    usage = "usage: %prog [options]\n\nParse data coming from a CurrentCost device."
    
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", dest="filename",help="write output to FILE (default: stdout)", metavar="FILE")
    parser.add_option("-s", "--serial-device", default='/dev/ttyUSB0',metavar="DEV",help="serial device to read from")
    parser.add_option("-i", "--interval",metavar="INT",type="int",default=300,help="interval in seconds over which data should be averaged (default:300)")
    parser.add_option("-d", "--daemon",action="store_true",default=False,help="run in daemon mode")
    parser.add_option("-p", "--pid-file",metavar="FILE",help="store PID in FILE")
    (options, args) = parser.parse_args()

    if options.daemon:
        if options.pid_file == None:
            parser.error('no pid file specified')
        if options.filename == None:
            parser.error('must specify output file')
            
        ourlockfile = lockfile.pidlockfile.PIDLockFile(options.pid_file)
        context = daemon.DaemonContext(
            working_directory='/tmp',
            umask=18 ,
            pidfile=ourlockfile
            )

        with context:
            readCurrentCost(options.serial_device,options.interval,options.filename)
    else:
        readCurrentCost(options.serial_device,options.interval,options.filename)
