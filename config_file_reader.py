import json
import os

from comm import getSupportedComms
from decide import Conf


class ConfigFileReader:
    """Class reading configuration settings from JSON file"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.supportedCommTypes = getSupportedComms()
        self.hosts = []

    def _check_hosts_names(self):

        hosts_to_del = dict()
        for host in self.hosts:
            name = host['host_name']
            hosts_to_del.setdefault(name, []).append(host) #in case it exists append to list host
                                                           # otherwise creates new list with host
        for values_to_del in hosts_to_del.values():
            if len(values_to_del) > 1:
                self._delete_hosts(values_to_del)

    def _check_comm_types(self):

        hosts_to_del = []
        for host in self.hosts:
            # convert all commtypes to lowercase to simplify checks on devices
            host['host_commtype'] = host['host_commtype'].lower()

            if host['host_commtype'] not in self.supportedCommTypes:
                print('%s host_commtype: %s is not supported' % (host['host_name'], host['host_commtype']))
                hosts_to_del.append(host)

        self._delete_hosts(hosts_to_del)

    def _check_conf_dirs(self):

        hosts_to_del = []
        for host in self.hosts:
            confdir = host["host_confdir"]
            if not os.path.isdir(confdir):
                print('%s host_confdir: %s is not directory' % (host['host_name'], confdir))
                hosts_to_del.append(host)
                continue

            readable = os.access(confdir, os.R_OK)  # check if conf directory is readable
            if readable is not True:
                print('%s host_confdir: %s is not readable' % (host['host_name'], confdir))
                hosts_to_del.ppend(host)
            else:
                conf = Conf.load(host)
                host['hook_register'] = conf.conf

        self._delete_hosts(hosts_to_del)

    def _handle_conflict_and_wrong(self, type, conflict, wrong):

        #here should be custom processing for confilc and wrong hosts
        #default behaviour - remove conflict and wrong hosts for all types from the list of hosts to be processed
        #instead of 'switch case', dictionary can be used and function of handling can be implemented
        #in apropriate source code from comm_type
        self._delete_hosts(conflict)
        self._delete_hosts(wrong)

    def _check_hosts_devs(self):

        concats = dict()
        for host in self.hosts:
            host_concat = host['host_commtype'] + host["host_commdev"]
            concats.setdefault(host_concat, []).append(host)

        for value in concats.values():
            # if couple hosts has equal combination type+dev
            if len(value) > 1:
                self._delete_hosts(value)


        #call check method for each host according to its commtype
        for comm_type, comm_type_details in self.supportedCommTypes.items():

            good = []
            conflict = []
            wrong = []

            #get hosts with devices of one type
            host_devs = [host for host in self.hosts if host["host_commtype"] == comm_type]
            comm_type_details[1](host_devs, good, conflict, wrong)

            #handle conflict and wrong devs for actual type
            self._handle_conflict_and_wrong(comm_type, conflict, wrong)

    def _add_indexes(self):
        for index, host in enumerate(self.hosts):
            host['host_index'] = index

    def _delete_hosts(self, hosts_to_delete):

        for host_to_del in hosts_to_delete:
            try:
                self.hosts.remove(host_to_del)
            except ValueError:
                pass # NOT AN ERROR - deleting non existing host from self.hosts
                     # one host can occur multiple times in list because of many checks
                     # so if host is not there its OK -> anyway, it may not be there

    def read_and_check_args(self):

        self.hosts = json.load(self.config_file)

        self._check_hosts_names() #remove hosts with duplicate names

        self._check_comm_types() #remove hosts with unsupported comm devs

        self._check_conf_dirs() #remove hosts with unreachable confdir

        self._check_hosts_devs() # check if compound of commtype + commdev is unique
                                  # to avoid situation that many hosts will be referencing
                                  # to 1 file / net interface etc.

        self._add_indexes() #add index for each host in list
