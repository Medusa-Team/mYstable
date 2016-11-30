import argparse

class Parser:
    _instance = None
    _default_conf_path = '/home/juraj/Documents/mYstable/config/medusa.conf'

    def __init__(self):
        if self._initialized is True:
            return

        self._parser = argparse.ArgumentParser()

        #here command line arguments should be specified
        self._add_commandline_argument()

        self._handle_arguments()
        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if Parser._instance is None:
            Parser._instance = object.__new__(cls)
            Parser._instance._initialized = False

        return Parser._instance

    def _add_commandline_argument(self):
        'Here should be specified arguments from commandline we want to work with'
        self._parser.add_argument("-c", "--config",
                                  metavar="<filename>",
                                  dest="config_file",
                                  default=Parser._default_conf_path,
                                  type=argparse.FileType('r'),
                                  help="sets path to configuration file")

    def _handle_arguments(self):

        arguments = self._parser.parse_args()
        attributes = arguments.__dict__

        for arg, value in attributes.items(): #loop in given arguments from command line and set attributes equal
            setattr(self, arg, value)         #to them

