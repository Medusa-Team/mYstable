import json
import  os

class ConfigFileReader:
    """Class reading configuration settings from JSON file"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.supported_comm_types = ('file',)
        self.hosts = []

    def _check_host_config(self, host):
        confdir = host["host_confdir"]
        if not os.path.isdir(confdir):
            raise NotADirectoryError("Directory '"+ confdir +"' does not exists")

        commtype = host["host_commtype"]
        if commtype.lower() not in self.supported_comm_types:
            raise NotImplementedError("host_commtype '" + commtype + "' is not supported")

        commdev = host["host_commdev"]


    def _check_hosts_names(self):
        host_names = set(host["host_name"] for host in self.hosts)

        if len(host_names) != len(self.hosts):
            raise AttributeError('Attribute "host_name" must be unique value')

    def read_args(self):
        #try:
        json_data = json.load(self.config_file)
        self.hosts = json_data["hosts"]

        #except json.JSONDecodeError as err:
         #   print(err.msg)
        #except KeyError as err:
         #   print(err.)
        #else:
        self._check_hosts_names()
        for host in self.hosts:
            self._check_host_config(host)




