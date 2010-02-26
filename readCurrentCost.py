from __future__ import with_statement
import serial
import time
from xml.dom import minidom
from optparse import OptionParser
import sys
import daemon,daemon.pidlockfile

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
    temp = 0.
    power = 0.
    count = 0
    
    while True:
        line = ser.readline()
        thisTime = time.time()
        if len(line)>0:
            xmldoc = minidom.parseString(line)
            # parse the xml
            try:
                temperature_nodes = xmldoc.getElementsByTagName('tmpr')
                watts_nodes = xmldoc.getElementsByTagName('ch1')[0].getElementsByTagName('watts')
            except:
                continue
            # accumulate data
            temp  += float(temperature_nodes[0].childNodes[0].nodeValue)
            power += float(watts_nodes[0].childNodes[0].nodeValue)
            count += 1
            # check if we should write out data
            if thisTime-startTime >= interval:
                outfile.write("%s %f %f\n"%(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(startTime+(thisTime-startTime)/2.)),temp/count, power/count))
                # reset counters
                count = 0
                temp = 0.
                power = 0.
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
            
        ourlockfile = daemon.pidlockfile.PIDLockFile(options.pid_file)
        context = daemon.DaemonContext(
            working_directory='/tmp',
            umask=18 ,
            pidfile=ourlockfile
            )

        with context:
            readCurrentCost(options.serial_device,options.interval,options.filename)
    else:
        readCurrentCost(options.serial_device,options.interval,options.filename)
