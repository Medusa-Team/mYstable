#!/usr/bin/python3

import threading
import argparse
import argparser

from mcp import doCommunicate

class constableThread(threading.Thread):
        def __init__(self, fnc):
                threading.Thread.__init__(self)
                self.fnc = fnc
        def run(self):
                self.fnc()

def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", metavar="<filename>", dest="config", help="sets path to configuration file")
        args = parser.parse_args()

        configFile = argparser.open_config_file(args)


'''     threads = []

        threads.append(constableThread(doCommunicate))

        for t in threads:
                t.start()

        for t in threads:
                t.join()

'''
if __name__ == "__main__":
        main()

