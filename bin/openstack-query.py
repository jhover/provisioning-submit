#!/bin/env python
import logging
import subprocess
import sys

print("openstack-query")

#
#            CLASSES
#
class NovaUsageEntry(object):
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
    return lines

def parseOpenstackCmdOutput(linelist):
    log = logging.getLogger()
    for line in linelist:
        log.debug('line="%s"' % line)
        line = line.strip()
    # Real output is on lines [3:-1]
    outlines = []
    if len(linelist) > 2:
        for line in linelist[3:-2]:
            log.debug('valid line="%s"' % line)
            fields = line.split()
            log.debug('fields="%s"' % fields)
            filteredfields = []
            for f in fields:
                if f == '|':
                    pass
                else:
                    filteredfields.append(f)
            outlines.append(filteredfields)
    return outlines

def getTenantList():
    log = logging.getLogger()
    cmd = 'keystone tenant-list'
    lines = runCommand(cmd)
    validlines = parseOpenstackCmdOutput(lines)
    
    #tl = []
    tl = validlines
    
    return tl

def getUsageList():
    log = logging.getLogger()
    cmd = 'nova usage-list'
    lines = runCommand(cmd)
    validlist = parseOpenstackCmdOutput(lines)
    return validlist


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
    ul = getUsageList()
    for u in ul:
        print(u)
        
