import json
import os

from comm import getSupportedComms
from comm_net import check_net_IP_duplicities
from comm_file import checkFiles

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
        """host_names = set(host["host_name"] for host in self.hosts)

        if len(host_names) != len(self.hosts):
            raise AttributeError('Attribute "host_name" must be unique value')
        """
        hosts_to_del = dict()
        for host in self.hosts:
            name = host['host_name']

            hosts_to_del.setdefault(name, []).append(host)

        for values_to_del in hosts_to_del.values():
            if len(values_to_del) > 1:
                self._delete_hosts(values_to_del)


    def _check_comm_types(self):

        hosts_to_del = []
        for host in self.hosts:
            # convert all commtypes to lowercase to simplify checks on devices
            host['host_commtype'] = host['host_commtype'].lower()
            if host['host_commtype'] not in self.supportedCommTypes:
                hosts_to_del.append(host)

        self._delete_hosts(hosts_to_del)

    def _check_conf_dirs(self):

        hosts_to_del = []
        for host in self.hosts:
            confdir = host["host_confdir"]
            if not os.path.isdir(confdir):
                hosts_to_del.append(host)
                continue

            readable = os.access(confdir, os.R_OK)  # check if conf directory is readable
            if readable is False:
                hosts_to_del.append(host)

        self._delete_hosts(hosts_to_del)

    def _check_hosts_devs(self):

        good = []
        conflict = []
        wrong = []

        devices = set(host['host_commtype']+host["host_commdev"] for host in self.hosts)

        if len(devices) != len(self.hosts):
            raise AttributeError('Combination of attributes "host_commtype" + "host_commdev" must be unique value')

        #call check method for each host regarding its commtype
        for comm_type, comm_type_details in self.supportedCommTypes.items():
            devices = [host["host_commdev"] for host in self.hosts if host["host_commtype"] == comm_type]
            (good, conflict, wrong) = comm_type_details[1](devices)

        pass

    def _delete_hosts(self, hosts_to_delete):
        for host in hosts_to_delete:
            self.hosts.remove(host)

    def read_and_check_args(self):

        self.hosts = json.load(self.config_file)

        self._check_hosts_names() #remove hosts with duplicate names

        self._check_comm_types() #remove hosts with unsupported comm devs

        self._check_conf_dirs() #remove hosts with unreachable confdir

        self._check_hosts_devs() # check if compound of commtype + commdev is unique
                                  # to avoid situation that many hosts will be referencing
                                  # to 1 file / net interface etc.
