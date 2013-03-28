# For all the awesomeness
import LabJackPython, sys
from urllib import urlopen
from ue9Upgrade import upgradeUe9Firmware
from u36Upgrade import upgradeU6Firmware, upgradeU3Firmware
from time import sleep
import getopt
import re # I know, I know

MAIN_FIRMWARE_URL = 'http://labjack.com/support/firmware'
FIRMWARE_DOWNLOAD_BASE_URL = 'http://labjack.com/sites/default/files'
U3C_LATEST_FIRMWARE_URL = 'http://files.labjack.com/versions/U3Cfirmware.txt'
U6_LATEST_FIRMWARE_URL = 'http://files.labjack.com/versions/U6firmware.txt'
UE9_LATEST_COMM_FIRMWARE_URL = 'http://files.labjack.com/versions/UE9comm.txt'
UE9_LATEST_CONTROL_FIRMWARE_URL = 'http://files.labjack.com/versions/UE9control.txt'


def findFirmware(places, version):
    for searchUrl in places:
        firmwareUrl, filename = getLatestFilename(searchUrl, version)
        if filename != '':
            return firmwareUrl, filename
    
    if filename == '':
        #print "Couldn't find firmware version %s.%s" % (version[0], version[1:])
        print "Couldn't find firmware version. Looked for file containing %s" % (version,)
        sys.exit(1)

def getLatestFilename(url, name):
    firmwarePattern = re.compile(r'''
                                "                    # The href attr starts with a quote
                                (                    # Remember the URL
                                %s                   # Base URL
                                /\d+/\d+/            # /YYYY/MM/
                                %s                   # filename prefix (the name passed in)
                                \w+                  # filename suffix (usually a date)
                                .(hex|bin)           # .hex or .bin
                                )                    # The href attr ends with a quote 
                                "''' % (FIRMWARE_DOWNLOAD_BASE_URL, name), re.VERBOSE)

    tagSoup = getUrl(url)
    m = firmwarePattern.search(tagSoup)
    if m:
        firmwareUrl = m.groups()[0] # Get the first matched part
        i = firmwareUrl.rfind('/')  # The filename is on the end after the slash
        filename = firmwareUrl[i+1:]
        return firmwareUrl, filename
    else:
        return '', ''

def downloadFwFromSite(url, filename):
    print "Downloading firmware from website..."
    data = getUrl(url)
    outfile = file(filename, "wb")
    outfile.write(data)
    outfile.close()
    print "Done."
        
def getUrl(url):
    l = urlopen(url)
    data = l.read()
    l.close()
    return data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python selfUpgrader [ -f <filename> ] [ -r ] [ -v <version number>] [--ip-address '192.168.1.209'] <devType>"
        sys.exit(1)
    
    optlist, args = getopt.getopt(sys.argv[1:], 'yrf:v:c:m:', 'ip-address=')
    
    devType = int(args[0])
    
    recovery = False
    fileNamed = False
    forceYes = False
    cOrM = False
    names = []
    version = None
    controlVersion = None
    commVersion = None
    ipAddress = None
    
    for o, v in optlist:
        if o == '-r':
            recovery = True
        if o == '-y':
            forceYes = True
        if o == '-f':
            fileNamed = True
            names.append(v)
            if (len(names) > 2 and devType == 9) or ( len(names) > 1 and devType != 9):
                raise Exception("Too many -fs.")
        if o == '-v':
            if devType == 9:
                raise Exception("Cannot use -v for UE9s please use -m <Comm Version> -c <Control Version>")
            version = v
        if o == '-m':
            if devType != 9:
                raise Exception("-m and -c are for UE9 only. Use -v for U3s and U6s.")
            commVersion= v
            cOrM = True
            
        if o == '-c':
            if devType != 9:
                raise Exception("-m and -c are for UE9 only. Use -v for U3s and U6s.")
            controlVersion = v
            cOrM = True
        if o == '--ip-address':
            if devType != 9:
                raise Exception("--ip-address is for UE9s only.")
            ipAddress = v 
            
    
    if devType == 3:
        if not fileNamed:
            if version is None:
                version = getUrl(U3C_LATEST_FIRMWARE_URL)
            version = version.replace('.','')
            
            url, filename = findFirmware([MAIN_FIRMWARE_URL+'/u3', MAIN_FIRMWARE_URL+'/u3/beta', MAIN_FIRMWARE_URL+'/u3/old'], "U3Cfirmware_%s" % version)
            
            print "Downloading firmware version %s.%s into a file called %s" % ( version[0], version[1:] ,filename)
            
            downloadFwFromSite(url, filename)
        else:
            filename = names[0]
        
        upgradeU3Firmware(filename, recovery, forceYes)
        
    elif devType == 6:
        if not fileNamed:
            if version is None:
                version = getUrl(U6_LATEST_FIRMWARE_URL)
            version = version.replace('.','')
            
            
            url, filename = findFirmware([MAIN_FIRMWARE_URL+'/u6', MAIN_FIRMWARE_URL+'/u6/beta', MAIN_FIRMWARE_URL+'/u6/old'], "U6firmware_%s" % version)
            
            print "Downloading firmware version %s.%s into a file called %s" % ( version[0], version[1:] ,filename)
            downloadFwFromSite(url, filename)
        else:
            filename = names[0]
        
        upgradeU6Firmware(filename, recovery, forceYes)
        
    elif devType == 9:
        places = [MAIN_FIRMWARE_URL+'/ue9', MAIN_FIRMWARE_URL+'/ue9/beta', MAIN_FIRMWARE_URL+'/ue9/clouddot', MAIN_FIRMWARE_URL+'/ue9/old']
        
        # Only upgrade the control firmware if it is specified.
        if controlVersion is not None or cOrM is False:
            if not fileNamed:
                if controlVersion is None:
                    controlVersion = getUrl(UE9_LATEST_CONTROL_FIRMWARE_URL)
                controlVersion = controlVersion.replace('.','')
                
                url, filename = findFirmware(places, "UE9control_%s" % controlVersion)
                
                print "The latest Control firmware is version %s.%s and is in the file called %s" % ( controlVersion[0], controlVersion[1:] , filename)
                
                downloadFwFromSite(url, filename)
            else:
                filename = names[0]
    
            upgradeUe9Firmware(filename, recovery, forceYes, ipAddress)
            print "Control firmware upgrade complete!\n\n"
            
        if commVersion is not None or cOrM is False:
            print "Begining upgrade of Comm firmware"
        
            if not fileNamed:
                if commVersion is None:
                    commVersion = getUrl(UE9_LATEST_COMM_FIRMWARE_URL)
                commVersion = commVersion.replace('.','')
                
                url, filename = findFirmware(places, "UE9comm_%s" % commVersion)
                
                print "The latest Comm firmware is version %s.%s and is in the file called %s" % ( commVersion[0], commVersion[1:] ,filename)
        
                downloadFwFromSite(url, filename)
            else:
                if len(names) == 2:
                    filename = names[1]
                else:
                    print "No Comm file specified. Exiting."
                    sys.exit(0)
            
            upgradeUe9Firmware(filename, False, forceYes, ipAddress)
            print "Upgrade success!"
    else:
        print "invalid devType."
