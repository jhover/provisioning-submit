#!/bin/env python

import subprocess

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

class NovaInstance(object):
    def __init__(self, ):
        self.
        
        
class GlanceImage(object):
    def __init__(self, imageid, name, format, container, size, status ):


#        
#        FUNCTIONS
#

def getTenantList():
    cmd = 'keystone tenant-list '
    log.debug("command= '%s'" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()    


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
        
        
        
