#!/usr/bin/python3

import threading
import argparser
import config_file_reader

from mcp import doCommunicate

class constableThread(threading.Thread):
        def __init__(self, fnc):
                threading.Thread.__init__(self)
                self.fnc = fnc
        def run(self):
                self.fnc()

def main():

        parser = argparser.Parser()
        conf_reader = config_file_reader.ConfigFileReader(parser.config_file)
        try:
            conf_reader.read_and_check_args()
        except Exception as err:
            for arg in err.args:
                print(arg)
            return

        comms = []
        for host_config in conf_reader.hosts:
            #get apropriate type of object for actual host_config
            comm_constructor = conf_reader.supportedCommTypes[host_config['host_commtype']][0]
            # create instance of apropriate 'comm' with apripriate config
            comms.append(comm_constructor(host_config))

        threads = []
        for comm in comms:
            threads.append(constableThread(doCommunicate(comm)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

if __name__ == "__main__":
        main()

