#!/usr/bin/env python 

#
# documentation on the python API:
#       http://docs.openstack.org/developer/python-novaclient/ref/v2/
#

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
 

VERSION = "2"
USERNAME = os.environ['OS_USERNAME']
PASSWORD = os.environ['OS_PASSWORD']
PROJECT_ID = os.environ['OS_TENANT_NAME']
AUTH_URL = os.environ['OS_AUTH_URL']
# FIXME !!
# these variables MUST exist in the environment
# check it before doing anything else



from novaclient import client

nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)


class MyImage:
    def __init__(self, id, name, image):
        
        self.id = id
        self.name = name
        self.image = image

    def __cmp__(self, i):
        if self.name < i.name:
            return -1
        elif self.name > i.name:
            return 1
        else:
            return 0



class MyNova:

    def get_vm_name(self):

        list_images = []
        
        for image in nova.images.list():
            list_images.append( MyImage(image.id, image.name, image) )
            
        list_images.sort()
        
        print "List of available VM images:"
        for i in range(len(list_images)):
            print "    %s%s %s%s : %s%s" %(bcolors.BOLD, bcolors.FAIL, i+1, bcolors.OKBLUE, list_images[i].name, bcolors.ENDC)
        
        
        index = raw_input("Pick one image type by typing the index number ")
        index = int(index)
        self.image_name = list_images[index-1].name
        self.image_id = list_images[index-1].id
        self.image = list_images[index-1].image
        
        username = pwd.getpwuid( os.getuid() )[ 0 ]
        date = time.strftime('%y%m%d')
        default_vm_name = "%s-%s-%s" %(self.image_name, username, date)
        self.vm_name = raw_input("Type a name for the VM instance (or hit ENTER for suggested name: %s) " %default_vm_name )
        if not self.vm_name:
            self.vm_name = default_vm_name



    def get_image_id(self):

        print "Instantiating VM %s ... (it may take a few seconds)" %self.vm_name
        flavor = nova.flavors.find(name='m1.medium')
        self.server = nova.servers.create(self.vm_name, self.image, flavor=flavor)
        
        while True:
            self.server = nova.servers.find(name=self.vm_name)
            status = self.server.status
            power = int(self.server.__dict__['OS-EXT-STS:power_state'])
            
            if status == "ACTIVE" and power == 1:
                self.vm_id = self.server.id
                break
         
            time.sleep(1)
        
        print "VM %s instantiated, with ID %s" %(self.vm_name, self.vm_id)
        
        
    def get_ip(self): 
        
        list_floating_ips = nova.floating_ips.list()
        for ip in list_floating_ips:
            if not ip.fixed_ip:
                self.ip = ip
                break

    
    def get_fixed_ip(self): 

        nova.servers.add_floating_ip(self.server, self.ip.ip)
        self.ip = nova.floating_ips.find(ip=self.ip.ip)
        

    def print_messages(self):

        print "now you can log into your new VM with command:"
        print "     ssh root@%s" %self.ip.ip
        print
        print "when finished, delete the VM with commands:"
        print "     nova stop %s" %self.vm_id
        print "     nova delete %s" %self.vm_id
        print


if __name__ == '__main__':
    mynova = MyNova()
    mynova.get_vm_name()
    mynova.get_image_id()
    mynova.get_ip()
    mynova.get_fixed_ip()
    mynova.print_messages()


