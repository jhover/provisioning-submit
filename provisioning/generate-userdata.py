#!/bin/env python
# 
# Takes in <profile>.yaml template files and embeds content of files into TDL-compilant XML files. 
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

from __future__ import print_function
import base64
import getopt
import logging
import os
import sys
import yaml

def handlefile(file, outfile= sys.stdout, profdir = None ):   
    log.debug("Handling file %s, profdir=%s" % (file, profdir))
    if outfile != sys.stdout:
        of = open(outfile, 'w')
    else:
        of = sys.stdout
    
    of.write("#cloud-config\nwrite_files\n")
        
    for file in files:
        with open(file, 'r') as f:
            doc = yaml.load(f)
            filepairs = doc['files']                
            for targetfile in filepairs.keys():
                sourcefile = filepairs[targetfile]
                if profdir:
                    sourcefile = "%s/%s" % (profdir, sourcefile)
                    log.debug("sourcefile path is %s" % sourcefile)
                else:
                    abspath = os.path.abspath(file)
                    filename = os.path.basename(abspath)
                    (filebase, ext) = os.path.splitext(filename)
                    profdir = filebase
                    sourcefile = "%s/%s" % (profdir, sourcefile)
                s = open(sourcefile, 'r')
                of.write("-   path: %s\n" % targetfile )
                of.write("    encoding: b64\n    owner: root:root\n    permissions: '0644'\n")
                encoded = base64.b64encode(s.readlines())
                of.write("    content: %s\n\n" % encoded)                
                log.debug('file content length: %d' % len(filecontent))
    of.close()


def ensurefile(filepath, clear = False):
    log.debug("Ensuring filepath %s" % filepath)
    filepath = os.path.expandvars(filepath)
    filepath = os.path.expanduser(filepath)
    d = os.path.dirname(filepath)
    if not os.path.exists(d):
        os.makedirs(d)
    if not os.path.exists(filepath):
        open(filepath, 'w').close()
    elif clear:
        open(filepath, 'w').close()


def main():  
    global log 
    debug = 0
    info = 0
    warn = 0
    filemaps = None
    profdir = None
    logfile = sys.stderr
    outfile = sys.stdout

    usage = """Usage: generate-userdata.py [OPTIONS] <files>.yaml  
   generate-userdata.py takes a YAML file map and creates a valid cloud-config
   userdata.txt file with the contents b64 encoded in a write_files: directive.  
     
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -V --version                Print program version and exit.
        -p --profile                <directory>.yaml
        -L --logfile                STDERR
        -o --outfile                STDOUT

     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvp:L:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "profile=",
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
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-o","--outfile"):
            outfile = arg
        elif opt in ("-p", "--profile"):
            profdir = arg
    
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
    filemaps = args
    log.debug("Args = %s" % filemaps)
    log.info("Handling files with Logfile=%s Outfile=%s and Profile=%s" % (logfile, outfile, profdir))    
    
    if filemaps:
        if outfile != sys.stdout:
            ensurefile(outfile, clear=True)
        for f in filemaps:
            handlefile(filemap, outfile, profdir )


if __name__ == "__main__":
    main()