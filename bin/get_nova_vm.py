#!/usr/bin/env python 

import commands
import os
import pwd
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class image:
    def __init__(self):
        self.id = ""
        self.name = ""


class nova:

    def get_vm_name(self):
    
        st, out = commands.getstatusoutput('nova image-list')
        #print st
        #print out
        
        list_images = []
        lines = out.split('\n')[3:-1]
        for line in lines:
            new_image = image()
            new_image.id = line.split()[1]
            new_image.name = line.split()[3]
            list_images.append(new_image)
    
        print "List of available VM images:"    
        for i in range(len(list_images)):
            print "    %s%s %s%s : %s" %(bcolors.BOLD, bcolors.FAIL, i+1, bcolors.ENDC, list_images[i].name)
        
        
        index = raw_input("Pick one image type by typing the index number ")
        index = int(index)
        self.image_name = list_images[index-1].name
        #print self.image_name
        self.image_id = list_images[index-1].id
        #print self.image_id
        
        
        username = pwd.getpwuid( os.getuid() )[ 0 ]
        date = time.strftime('%y%m%d') 
        default_vm_name = "%s-%s-%s" %(self.image_name, username, date)
        self.vm_name = raw_input("Type a name for the VM instance (or hit ENTER for default: %s) " %default_vm_name )
        if not self.vm_name:
            self.vm_name = default_vm_name
        #print self.vm_name
        
        
        
    def get_image_id(self):

        print "Instantiating VM %s... (it may take a few seconds)" %self.vm_name
        st, out = commands.getstatusoutput('nova boot %s --flavor m1.medium --image %s --security-groups default' %(self.vm_name, self.image_id))
        #print st
        #print out
        
        while True:
            st, out = commands.getstatusoutput('nova list --name ^%s$ --fields status,OS-EXT-STS:power_state' %self.vm_name)
            #print st
            #print out
            lines = out.split('\n')
            line = lines[3]
            #print line
            status = line.split()[3]
            power = line.split()[5]
            
            if status == "ACTIVE" and power == '1':
                self.vm_id = line.split()[1]
                break
         
            time.sleep(3)
        
        print "VM %s instantialted, with ID %s" %(self.vm_name, self.vm_id)
        
        
    def get_ip(self): 
        
        st, out = commands.getstatusoutput('nova floating-ip-list')
        #print st
        #print out
        
        lines = out.split('\n')[3:-1]
        #print lines
        
        self.ip = None
        for line in lines:
            if line.split()[4] == '-':
                self.ip = line.split()[1]
                break
        
        #print self.ip 
        
    
    def get_fixed_ip(self): 
        
        st, out = commands.getstatusoutput('nova floating-ip-associate %s %s' %(self.vm_id, self.ip))
        #print st
        #print out
        
        
        st, out = commands.getstatusoutput('nova floating-ip-list')
        #print st
        #print out
        lines = out.split('\n')[3:-1]
        for line in lines:
            if line.split()[1] == self.ip:
                self.fixed_ip = line.split()[4]
        
        
        #print self.fixed_ip



nova = nova()
nova.get_vm_name()
nova.get_image_id()
nova.get_ip()
nova.get_fixed_ip()

print "now you can log into your new VM with command:"
print "     ssh root@%s" %nova.fixed_ip
print
print "when finished, delete the VM with commands:"
print "     nova stop %s" %nova.vm_id
print "     nova delete %s" %nova.vm_id
print



