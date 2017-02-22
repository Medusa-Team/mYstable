import json
import os

from comm import getSupportedComms
from comm_net import check_net_IP_duplicities

class ConfigFileReader:
    """Class reading configuration settings from JSON file"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.supportedCommTypes = getSupportedComms()
        self.hosts = []

    def _check_host_config(self, host):
        #nie je asi dobre zhadzovat celu meduzu ak je len jeden host zly.
        #treba ho len odobrat a pokracovat v kontrole ostatnych nie?

        commtype = host["host_commtype"]
        if commtype not in self.supportedCommTypes:
            raise NotImplementedError("host_commtype '" + commtype + "' is not supported")

        confdir = host["host_confdir"]
        if not os.path.isdir(confdir):
            raise NotADirectoryError("Directory '"+ confdir +"' does not exists")

        readable = os.access(confdir,os.R_OK) #check if conf directory is readable
        if readable is False:
            raise AttributeError("Directory '" + confdir + "' is not read accessible for Meduza.")



    def _check_hosts_names(self):
        host_names = set(host["host_name"] for host in self.hosts)

        if len(host_names) != len(self.hosts):
            raise AttributeError('Attribute "host_name" must be unique value')

    def _check_hosts_devs(self):
        devices = set(host["host_commtype"]+host["host_commdev"] for host in self.hosts)

        if len(devices) != len(self.hosts):
            raise AttributeError('Combination of attributes "host_commtype" + "host_commdev" must be unique value')

        #call check method for each host regarding its commtype
        for comm_type, comm_type_details in self.supportedCommTypes.items():
            comm_type_details[1]([host["host_commdev"] for host in self.hosts if host["host_commtype"].lower() == comm_type])


    def read_and_check_args(self):

            self.hosts = json.load(self.config_file)

            # convert all commtypes to lowercase to simplify later checks + add indicies
            for index,host in enumerate(self.hosts):
                host['host_commtype'] = host['host_commtype'].lower()
                host['host_index'] = index

            self._check_hosts_names() #check if hostname is unique

            for host in self.hosts:
                self._check_host_config(host) # check if host has supported commtype
                                              # and if confdir is readable

            check_net_IP_duplicities(self.hosts)  # check if each net host has unique net device
            self._check_hosts_devs() # check if compound of commtype + commdev is unique
                                     # to avoid situation that many hosts will be referencing
                                     # to 1 file / net interface etc.
