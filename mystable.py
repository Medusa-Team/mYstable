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
        conf_reader.read_args()

'''     threads = []

        threads.append(constableThread(doCommunicate))

        for t in threads:
                t.start()

        for t in threads:
                t.join()

'''
if __name__ == "__main__":
        main()

