#!/bin/env python
import logging
import subprocess
import sys

print("openstack-query")

#
#            CLASSES
#
class NovaUsageList(object):
    def __init__(self, tenantid, numservers, rammbhrs, cpuhrs, diskgbhrs):
        self.tenantid = tenantid
        self.numservers = numservers
        self.rammbhrs = rammbhrs
        self.cpuhrs = cpuhrs
        self.diskgbhrs = diskgbhrs 
    
class KeystoneTenant(object):
    def __init__(self, tenantid, name, enabled ):
        self.tenantid = tenantid
        self.name = name
        self.enabled = enabled
    
    def __str__(self):
        s = ""
        s += "id=%s, name=%s" % (self.tenantid, self.name)
        return s

class NovaInstance(object):
    def __init__(self, id, name, status, power, networks ):
        self.id = ie
        self.name = name
        self.status = status
        self.power = power
        self.networks = networks
        
        
class GlanceImage(object):
    def __init__(self, imageid, name, format, container, size, status ):
        self.imageid = imageid
        self.name = name
        self.format = format
        self.container = container
        self.size = size
        self.status = status
        

#        
#        FUNCTIONS
#
def runCommand(cmd):
    log = logging.getLogger()
    log.debug("command= '%s'" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()    
    lines = out.split('\n')
    num = len(lines)
    log.info("Got %d lines of output." % num)
    for line in lines:
        log.debug('line="%s"' % line)
        line = line.strip()



def getTenantList():
    cmd = 'keystone tenant-list'
    lines = runCommand(cmd)
    tl = []
    # Real output is on lines [3:-1]
    if len(lines) > 2:
        for line in lines[3:-1]:
            log.debug('valid line="%s"' % line)
    return tl

def setupLogging():
    log = logging.getLogger()
    formatstr="[%(levelname)s] %(asctime)s %(module)s.%(funcName)s(): %(message)s"
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(formatstr)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

    

if __name__ == '__main__':
    setupLogging()
    tl = getTenantList()    
    for t in tl:
        print(t)
        
