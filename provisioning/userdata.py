#!/bin/env python
from __future__ import print_function

# 
# Takes in yaml map OR a root directory, and embeds all files/paths within into
# a cloud-init compatible userdata file  
#
#  files:
#     "/path/to/file/filename1.txt" : "local/relative/path/file.txt"
#     "/path/to/file/filename2.txt" : "local/relative/path/file2.txt"
# 
#  PRODUCES --->
#
#  #cloud-config
#  write_files:
#
#    - path: /path/to/file/filename1.txt 
#      permissions: 0644
#      owner: root
#      encoding: base64
#      content: |
#        UGFjayBteSBib3ggd2l0aCBmaXZlIGRvemVuIGxpcXVvciBqdWdz
#
#    - path: /path/to/file/filename2.txt 
#      permissions: 0644
#      owner: root
#      encoding: base64
#      content: |
#        UGFjayBteSBib3ggd2l0aCBmaXZlIGRvemVuIGxpcXVvciBqdWdz
#
#! /usr/bin/env python

__author__ = "John Hover"
__copyright__ = "2016 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.99"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"


import base64
import getopt
import logging
import os
import sys
import yaml


class UserDataLib(object):
    
    def __init__(self, outfile, filemaps, rootdirs):
        self.log = logging.getLogger()
        self.filemaps = filemaps
        self.rootdirs = rootdirs
        self.outfile = outfile
        try:
            self.outfile = os.path.expanduser(outfile)
        except AttributeError:
            # item may be stdout rather than a filename 
            pass        
        self.outfileh = None


    def handleall(self):
        # prepare output file
        if self.outfile != sys.stdout:
            self.log.debug("outfile isn't stdout, opening real file...")
            self.outfileh = open(self.outfile, 'w')
        else:
            self.log.debug("outfile is stdout")
            self.outfileh = sys.stdout
    
        self.outfileh.write("#cloud-config\nwrite_files:\n\n")
        
        for d in self.rootdirs:
            self.handledir(d)
        for fm in self.filemaps:
            self.handlefile(fm)
        
        if self.outfileh != sys.stdout:
            self.log.debug("Closing output file %s" % outfile)
            selfoutfileh.close()
    
    def handledir(self, rootdir):
        self.log.debug("Handling directory %s" % rootdir)
        

    def handlefile(self, filemap ):   
        self.log.debug("Handling file %s" % filemap)
        fp = os.path.realpath(filemap)
        self.log.debug("Filemap full path is %s " % fp)
        (profdir, yamlfile) = os.path.split(fp)
        self.log.debug("Profdir is %s, yamlfilename is %s "% (profdir, yamlfile))
        #(yfn, ext) = os.path.splitext(yamlfile)
        #self.log.debug("profile basedir name is %s" % yfn)
        #profdir = os.path.join(profdir, yfn )
        self.log.debug("Filemap rootdir is %s" % profdir)
        with open(filemap, 'r') as f:
            doc = yaml.load(f)
            filepairs = doc['files']                
            for targetfile in filepairs.keys():
                self.log.debug("targetfile = %s" % targetfile)
                sourcefile = filepairs[targetfile]
                self.log.debug("sourcefile = %s" % sourcefile)
                sourcefile = os.path.join(profdir, sourcefile)
                self.log.debug("Opening sourcefile %s" % sourcefile)
                s = open(sourcefile, 'r')
                self.outfileh.write("-   path: %s\n" % targetfile )
                #of.write("    encoding: b64\n    owner: root:root\n    permissions: '0644'\n")
                #
                # Files may contain passwords, so maybe they should be readable only by root?
                #
                self.outfileh.write("    encoding: b64\n    owner: root:root\n    permissions: '0600'\n")
                encoded = base64.b64encode(s.read())
                self.outfileh.write("    content: %s\n\n" % encoded)
                s.close()
                self.log.debug("Finished with source %s dest %s" % (sourcefile, targetfile))
        f.close()
        self.log.debug("Closed yaml file %s" % file)                

    
def main():  
    global log 
    debug = 0
    info = 0
    warn = 0
    rootdirs = []
    filemaps = []
    logfile = sys.stderr
    outfile = sys.stdout

    usage = """Usage: userdata.py [OPTIONS]  
   userdata.py takes one or more YAML file maps and/or one or more root 
   directories, merges them all, and creates a valid cloud-config
   userdata.txt file with the contents b64 encoded in a write_files: directive.
       
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -v --verbose                Verbose messages
        -V --version                Print program version and exit.
        -f --filemaps                filemap.yaml [filemap2.yaml ...] 
        -r --rootdirs                ./  [ path/to/root2 path/to/root3
        -L --logfile                STDERR
        -o --outfile                STDOUT
     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvVf:r:L:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "version",
                                    "filemap=",
                                    "rootdir=",
                                    "logfile=",
                                    "outfile=",
                                    ])
    except getopt.GetoptError, error:
        print( str(error))
        print( usage )                          
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)                     
            sys.exit()            
        elif opt in ("-d", "--debug"):
            debug = 1
        elif opt in ("-v", "--verbose"):
            info = 1
        elif opt in ("-V", "--version"):
            print(__version__)
            sys.exit(0)
        elif opt in ("-f", "--filemap"):
            filemaps.append( arg )
        elif opt in ("-r", "--rootdir"):
            rootdirs.append( arg )
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-o","--outfile"):
            outfile = arg

    
    major, minor, release, st, num = sys.version_info
    FORMAT24="[ %(levelname)s ] %(asctime)s %(filename)s (Line %(lineno)d): %(message)s"
    FORMAT25="[%(levelname)s] %(asctime)s %(module)s.%(funcName)s(): %(message)s"
    FORMAT26=FORMAT25
    FORMAT27=FORMAT26
    
    if major == 2:
        if minor == 4:
            formatstr = FORMAT24
        elif minor == 5:
            formatstr = FORMAT25
        elif minor == 6:
            formatstr = FORMAT26
        elif minor == 7:
            formatstr = FORMAT27
    else:
        formatstr = FORMAT27
            
    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(formatstr)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    # Handle file-based logging.
    if logfile != sys.stderr:
        ensurefile(logfile)        
        hdlr = logging.FileHandler(logfile)
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)

    if warn:
        log.setLevel(logging.WARN)
    if debug:
        log.setLevel(logging.DEBUG) # Override with command line switches
    if info:
        log.setLevel(logging.INFO) # Override with command line switches

    log.debug("%s" %sys.argv)
    log.info("Running with Logfile=%s Outfile=%s" % (logfile, 
                                                     outfile))    
    
        
    udobj = UserDataLib(outfile, filemaps, rootdirs)
    udobj.handleall()


if __name__ == "__main__":
    main()