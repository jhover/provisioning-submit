#!/bin/env python
import logging
import subprocess
import sys
import traceback

print("openstack-query")

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
 

class QueryCLI(object):
    def __init__(self):
        self.parseopts()
        self.setuplogging() 
        self.novaquery = NovaQuery()
    
    def parseopts(self):
        parser = argparse.ArgumentParser()
        
        parser.add_argument('-d', '--debug', 
                            action="store_true", 
                            dest='debug', 
                            help='debug logging')        

        parser.add_argument('-v', '--verbose', 
                            action="store_true", 
                            dest='verbose', 
                            help='verbose/info logging')            
        
        # Init sub-command
        subparsers = parser.add_subparsers( dest="subcommand")

        parser_occupancy = subparsers.add_parser('occupancy', 
                                                help='create new vc3 user')
        
        parser_usagestats = subparsers.add_parser('usagestats', 
                                                help='list vc3 user(s)')
        
        self.results= parser.parse_args()



    def setuplogging(self):
        self.log = logging.getLogger()
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        #formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.StreamHandler()
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
    
        self.log.setLevel(logging.WARN)
        if self.results.debug:
            self.log.setLevel(logging.DEBUG)
        if self.results.verbose:
            self.log.setLevel(logging.INFO)
        self.log.info('Logging initialized.')

 
    def doQuery(self):
        '''
        Perform query and print. 

        '''
        self.test()
        

    def test(self):
        print("doquery test")
        print(self.results)
        
        try:
            hl = self.novaquery.getHypervisors()
            print(hl)
        except Exception, e:
            self.log.error("failed getHypervisors")

        try:
            tl = self.novaquery.getTenantList()
            print(tl)
        except Exception, e:
            self.log.error("failed getTenantList")

        try:
            ul = self.novaquery.getUsageList()
            print(ul)
        except Exception, e:
            self.log.error("failed getUsageList")

        try:
            s = self.novaquery.getUsageTable()
            print(s)
        except Exception, e:
            self.log.error("failed getUsageTable")


class NovaQuery(object):
    
    def __init__(self):
        self.log = logging.getLogger()
        

    def runCommand(self, cmd):
        self.log.debug("command= '%s'" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()    
        lines = out.split('\n')
        num = len(lines)
        self.log.info("Got %d lines of output." % num)
        for line in lines:
            self.log.debug('line="%s"' % line)
            line = line.strip()
        return lines
    
    
    def parseOpenstackCmdOutput(self, linelist):

        for line in linelist:
            self.log.debug('line="%s"' % line)
            line = line.strip()
        # Real output is on lines [3:-1]
        outlines = []
        if len(linelist) > 2:
            for line in linelist[3:-2]:
                self.log.debug('valid line="%s"' % line)
                fields = line.split()
                self.log.debug('fields="%s"' % fields)
                filteredfields = []
                for f in fields:
                    if f == '|':
                        pass
                    else:
                        filteredfields.append(f)
                outlines.append(filteredfields)
        return outlines
    
    def getTenantList(self):
        cmd = 'keystone tenant-list'
        tl = []
        lines = self.runCommand(cmd)
        validfields = self.parseOpenstackCmdOutput(lines)
        for vf in validfields:
            kt = KeystoneTenant(vf[0],
                               vf[1],
                               vf[2],
                               )
            tl.append(kt)
        return tl
    
    def getUsageList(self):
        '''
        +----------------------------------+---------+--------------+-----------+---------------+
        | Tenant ID                        | Servers | RAM MB-Hours | CPU Hours | Disk GB-Hours |
        +----------------------------------+---------+--------------+-----------+---------------+
        | 42d695a03a55476aa4e5383c4edec5b2 | 36      | 664875100.03 | 319270.03 | 24588467.99   |
        | cd08640af17d4b018b1462b130685b0b | 1       | 1376259.13   | 672.00    | 13440.03      |
        | cf29159fc3dd4ba9b59993f048397a79 | 2       | 22020146.10  | 10752.02  | 6733455.32    |
        | a629decc3bc8411a83cc210326db829c | 1       | 2752518.26   | 1344.00   | 26880.06      |
        | 0c342741b8de4bfbb5d19f381f6096a7 | 1       | 11010073.05  | 5376.01   | 3366727.66    |
        | dad1a42cc70b4949b355aed5889c470a | 189     | 670965543.53 | 306181.77 | 21490843.28   |
        | 77cc7601e9dd497ca0383e6f5051a005 | 3       | 999.54       | 0.49      | 9.76          |
        +----------------------------------+---------+--------------+-----------+---------------+
    
        
        '''
        cmd = 'nova usage-list'
        ul = []
        lines = self.runCommand(cmd)
        # usage-list has one extra line at the top. 
        lines=lines[1:]
        validlist = self.parseOpenstackCmdOutput(lines)
        for vf in validlist:
            self.log.debug("vf = %s" % vf)
            ue = NovaUsageEntry(vf[0],
                                vf[1],
                                vf[2],
                                vf[3],
                                vf[4],
                                )
            ul.append(ue)
        return ul
    
    
    def getHypervisors(self):
        '''
        nova hypervisor-list
        +-----+----------------------+
        | ID  | Hypervisor hostname  |
        +-----+----------------------+
        | 1   | cldh0188.cloud.local |
        | 2   | cldh0189.cloud.local |
        | 3   | cldh0190.cloud.local |
        +-----+----------------------+
        '''
        cmd = 'nova hypervisor-list'
    
    
    
    #
    # Servers | RAM MB-Hours | CPU Hours | Disk GB-Hours
    #
    def getUsageTable():
        tl = self.getTenantList()    
        indexbyid = {}
        for t in tl:
            indexbyid[t.tenantid] = t
        ul = self.getUsageList()
        s = ""
        for u in ul:
            tname = indexbyid[u.tenantid].name
            # numservers, rammbhrs, cpuhrs, diskgbhrs
            s += '%s\t%s\t%s\t%s\t%s ' % (tname, 
                                        u.numservers, 
                                        u.rammbhrs, 
                                        u.cpuhrs, 
                                        u.diskgbhrs)
        return s

  

if __name__ == '__main__':

    qcli = QueryCLI()
    qcli.doquery()



        
