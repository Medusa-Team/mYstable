#!/usr/bin/python3

import threading
import argparser
import config_file_reader

from mcp import doCommunicate


class ConstableThread(threading.Thread):

    def __init__(self, fnc, *args, **kwargs):
        threading.Thread.__init__(self, daemon=False)
        #super().__init__(daemon=False)
        self.fnc = fnc
        self.comm = kwargs['comm']
        self.fnc(self.comm)

    def run(self):
        self.fnc(self.comm)


def main():

    parser = argparser.Parser()
    conf_reader = config_file_reader.ConfigFileReader(parser.config_file)
    try:
        conf_reader.read_and_check_args()
    except Exception as err:
        for arg in err.args:
            print(arg)
            return

    if len(conf_reader.hosts) == 0:
        #TODO info message!!!
        return

    threads = []
    for host_config in conf_reader.hosts:
        # get apropriate type of object for actual host_config
        comm_constructor = conf_reader.supportedCommTypes[host_config['host_commtype']][0]
        # create instance of apropriate 'comm' with apripriate config
        comm = comm_constructor(host_config)

        threads.append(ConstableThread(doCommunicate, comm=comm))

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
