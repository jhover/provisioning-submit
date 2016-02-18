#!/usr/bin/env python 

#################################################################
#   FIXME !!!
#   the split into classes MyNova and MyNovaUserInterface
#   was not done properly
#   the core class MyNova should not have any call to the 
#   UserInterface class
#   it should be the opposite: the UI class calls the core class
#################################################################


#
# documentation on the python API:
#       http://docs.openstack.org/developer/python-novaclient/ref/v2/
#

#
#  NOTE
#   interactive tests
#   
#   $ cd /usr/lib/python2.6/site-packages/novaclient
#   $ python
#   >>> 
#   >>> import os
#   >>> import pwd 
#   >>> import sys 
#   >>> import time
#   >>> 
#   >>> VERSION = "2" 
#   >>> USERNAME = os.environ['OS_USERNAME']
#   >>> PASSWORD = os.environ['OS_PASSWORD']
#   >>> PROJECT_ID = os.environ['OS_TENANT_NAME']
#   >>> AUTH_URL = os.environ['OS_AUTH_URL']
#   >>> 
#   >>> import client
#   >>> nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
#   >>> 
#   >>> print nova.flavors.list()
#   ...
#

import commands
import logging
import os
import pwd
import sys
import time

# FIXME: 
# what to do if the import fails?
from novaclient import client


class MyNovaUserInterface(object):

    def __init__(self, verbosity):

        class BColors:
            #
            # WARNING:
            # problem with colors is that if we add a handler to the logger
            # to print messages to a file, 
            # the file get filled with nasty mark symbols
            #
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        self.bcolors = BColors()
        self.verbosity = verbosity
        self._getlogger()

    def _getlogger(self):

        self.log = logging.getLogger('userinterface')
        logStream = logging.StreamHandler()
        #FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        FORMAT='%(message)s'
        formatter = logging.Formatter(FORMAT)
        formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(self.verbosity)


    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        self.log.critical(msg)


    def select_image(self, list_images):
        return self._select_from_list(list_images, "VM images")

    def select_flavor(self, list_flavors):
        return self._select_from_list(list_flavors, "image flavors")

    def select_delete(self, list_servers):
        return self._select_from_list(list_servers, "VM instances (servers) currently running")
    

    def select_name(self, image_name):

        username = pwd.getpwuid( os.getuid() )[ 0 ]
        date = time.strftime('%y%m%d')
        default_vm_name = "%s-%s-%s" %(image_name, username, date)
        vm_name = raw_input("Type a name for the VM instance (or hit ENTER for suggested name: %s) " %default_vm_name )
        if not vm_name:
            vm_name = default_vm_name
        return vm_name


    def create_final_message(self, ip, vm_id):

        self.log.info("now you can log into your new VM with command:")
        self.log.info("     ssh root@%s" %ip.ip)
        self.log.info("")
        self.log.info("when finished, delete the VM with commands:")
        self.log.info("     nova stop %s" %vm_id)
        self.log.info("     nova delete %s" %vm_id)
        self.log.info("or running this script with 'delete' option")
        self.log.info("")


    def _select_from_list(self, list_items, item_type):
        """
        generic method to display a list of options 
        on the stdout, 
        and let the user to pick one by index number
        """

        self.log.info("List of available %s:" %item_type)
        for i in range(len(list_items)):
            self.log.info("    %s%s %s%s : %s%s" %(self.bcolors.BOLD, self.bcolors.FAIL, i+1, self.bcolors.OKBLUE, list_items[i].name, self.bcolors.ENDC))
        index = raw_input("Pick one by typing the index number: ")
        index = int(index)
        return index




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

    def __init__(self):

        self._parseopts()
        self._getlogger()
        
        try:
            self._setenvironment()
        except KeyError, k:
            self.log.critical('mandatory variable %s is not defined in the environment', k)
            raise Exception

        self.nova = client.Client(self.VERSION, self.USERNAME, self.PASSWORD, self.PROJECT_ID, self.AUTH_URL)

        self.ui = MyNovaUserInterface(self.verbosity)


    def _parseopts(self):
        """
        TO BE IMPLEMENTED !!!
        """
        # FIXME
        self.verbosity = logging.DEBUG


    def _getlogger(self):
        self.log = logging.getLogger('mynova')
        logStream = logging.StreamHandler()
        #FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        FORMAT='%(message)s'
        formatter = logging.Formatter(FORMAT)
        formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(self.verbosity)


    def _setenvironment(self):

        self.VERSION = "2"
        self.USERNAME = os.environ['OS_USERNAME']
        self.PASSWORD = os.environ['OS_PASSWORD']
        self.PROJECT_ID = os.environ['OS_TENANT_NAME']
        self.AUTH_URL = os.environ['OS_AUTH_URL']

    def usage(self):

        self.log.info('')
        self.log.info('Tool to facilitate instantiating a VM with nova.')
        self.log.info('Usage:')
        self.log.info('')
        self.log.info('$ python get_nova_vm_api.py create|delete')
        self.log.info('')


    def create(self):

        self._get_vm_name()
        self._get_image_id()
        self._get_ip()
        self._print_create_final_message()


    def _get_list_images(self):

        list_images = []

        for image in self.nova.images.list():
            if image.status == "ACTIVE":
                list_images.append( MyImage(image.id, image.name, image) )

        list_images.sort()
        return list_images

    def _set_iamge_properties(self, image):

        self.image_name = image.name
        self.image_id = image.id
        self.image = image.image


    def _get_vm_name(self):

        list_images = self._get_list_images()

        index = self.ui.select_image(list_images)

        image = list_images[index-1]
        
        self.vm_name = self.ui.select_name(self.image_name)


    def _get_image_id(self):

        self.ui.info("Instantiating VM %s ... (it may take a few seconds)" %self.vm_name)

        #
        #   >>> nova.flavors.list()
        #   [<Flavor: m1.tiny>, <Flavor: m1.small>, <Flavor: m1.medium>, <Flavor: m1.large>, <Flavor: m1.xlarge>, <Flavor: m1.xlarge.160>, <Flavor: m1.2xlarge.750>, <Flavor: m1.2xlarge.500>, <Flavor: m1.2xlarge.700>]
        #
        #   >>> f = nova.flavors.list()[0]
        #   >>> print f
        #   <Flavor: m1.tiny>
        #
        #   >>> print f.name
        #   m1.tiny
        #
        #   >>> print f.__dict__
        #   {'name': u'm1.tiny', 'links': [{u'href': u'http://192.153.161.7:8774/v2/a629decc3bc8411a83cc210326db829c/flavors/1', u'rel': u'self'}, {u'href': u'http://192.153.161.7:8774/a629decc3bc8411a83cc210326db829c/flavors/1', u'rel': u'bookmark'}], 'ram': 512, 'vcpus': 1, 'id': u'1', 'OS-FLV-DISABLED:disabled': False, 'manager': <novaclient.v1_1.flavors.FlavorManager object at 0x10fced0>, 'swap': u'', 'os-flavor-access:is_public': True, 'rxtx_factor': 1.0, '_info': {u'name': u'm1.tiny', u'links': [{u'href': u'http://192.153.161.7:8774/v2/a629decc3bc8411a83cc210326db829c/flavors/1', u'rel': u'self'}, {u'href': u'http://192.153.161.7:8774/a629decc3bc8411a83cc210326db829c/flavors/1', u'rel': u'bookmark'}], u'ram': 512, u'OS-FLV-DISABLED:disabled': False, u'vcpus': 1, u'swap': u'', u'os-flavor-access:is_public': True, u'rxtx_factor': 1.0, u'OS-FLV-EXT-DATA:ephemeral': 0, u'disk': 1, u'id': u'1'}, 'disk': 1, 'OS-FLV-EXT-DATA:ephemeral': 0, '_loaded': True}
        #   

        list_flavors = self.nova.flavors.list()
        index = self.ui.select_flavor(list_flavors)

        name = list_flavors[index-1].name
        #flavor = self.nova.flavors.find(name='m1.medium')
        # FIXME:
        #   make 'm1.medium' the default
        flavor = self.nova.flavors.find(name=name)
        self.server = self.nova.servers.create(self.vm_name, self.image, flavor=flavor)
        #print ">>>>>>>>>>>>>>>>>"
        #print dir(self.server)
        #print
        #print self.server.__dict__
        #print ">>>>>>>>>>>>>>>>>"
       
        self.ui.info('Instantiating VM... (this step will take a few seconds)')
 
        while True:
            self.server = self.nova.servers.find(name=self.vm_name)
            status = self.server.status
            power = int(self.server.__dict__['OS-EXT-STS:power_state'])
            
            if status == "ACTIVE" and power == 1:
                self.vm_id = self.server.id
                break
         
            time.sleep(1)

        #print ">>>>>>>>>>>>>>>>>"
        #print dir(self.server)
        #print
        #print self.server.__dict__
        #print ">>>>>>>>>>>>>>>>>"
        
        self.ui.info("VM %s instantiated, with ID %s" %(self.vm_name, self.vm_id))
       

    def _get_ip(self):

        self._get_floating_ip() 
        self._get_fixed_ip()
        

    def _get_floating_ip(self): 
        
        list_floating_ips = self.nova.floating_ips.list()
        # search for the first available IP not yet picked up
        for ip in list_floating_ips:
            if not ip.fixed_ip:
                self.ip = ip
                break

    
    def _get_fixed_ip(self): 

        self.nova.servers.add_floating_ip(self.server, self.ip.ip)
        self.ip = self.nova.floating_ips.find(ip=self.ip.ip)
        

    def _print_create_final_message(self):
        self.ui.create_final_message(self.ip, self.vm_id)


    def delete(self):

        list_servers = self.nova.servers.list()
        index = self.ui.select_delete(list_servers)
        server = list_servers[index-1]
        self.ui.info("Deleting VM instance with name %s ..." %server.name)
        server.stop()
        server.delete()
        self.ui.info("VM instance with name %s deleted" %server.name)


    
    

if __name__ == '__main__':

    # FIXME!!
    # this needs to be done properly, with argparse, getopt, or similar.

    try:
        mynova = MyNova()
    except:
        # FIXME
        pass
        
    if len(sys.argv) != 2:
        mynova.usage()
        sys.exit()    
    
    if sys.argv[1] == 'create':
        mynova.create()
    elif sys.argv[1] == 'delete':
        mynova.delete()
    else:
        #FIXME
        sys.exit()    
    


