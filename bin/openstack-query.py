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
    def __init__(self, instanceid, name, status, power, networks ):
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
    tl = []
    lines = runCommand(cmd)
    validfields = parseOpenstackCmdOutput(lines)
    for vf in validfields:
        kt = KeystoneTenant(vf[0],
                           vf[1],
                           vf[2],
                           )
        tl.append(kt)
    return tl

def getUsageList():
    log = logging.getLogger()
    cmd = 'nova usage-list'
    ul = []
    lines = runCommand(cmd)
    validlist = parseOpenstackCmdOutput(lines)
    for vf in validlist:
        log.debug("vf = %s" % vf)
        ue = NovaUsageEntry(vf[0],
                            vf[1],
                            vf[2],
                            vf[3],
                            vf[4],
                            )
        ul.append(ue)
    return ul



#
# Servers | RAM MB-Hours | CPU Hours | Disk GB-Hours
#
def printUsageList():
    tl = getTenantList()    
    indexbyid = {}
    for t in tl:
        indexbyid[t.tenantid] = t
    ul = getUsageList()
    for u in ul:
        tname = indexbyid[u.tenantid]
        # numservers, rammbhrs, cpuhrs, diskgbhrs
        print('%s\t%s\t%s\t%s\t%s ' % (tname, 
                                    u.numservers, 
                                    u.rammbhrs, 
                                    u.cpuhrs, 
                                    u.diskgbhrs))



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
    printUsageList()

        
