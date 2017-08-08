from constants import MED_OK, MED_NO
from importlib import import_module

class Rules():
    rules = {}
    def load(host):
        conf_dir = host['host_confdir']
        if conf_dir in Rules.rules:
            return Rules.rules[conf_dir]
        rules = Rules(host)
        Rules.rules[conf_dir] = rules

        return rules

    def __init__(self, host):
        conf_dir = host['host_confdir']

        rules = None
        try:
            rules_module = import_module(conf_dir.replace('/', '.'), package=None)
            rules_module.__dict__['hostname'] = host['host_name']
            rules = rules_module.register.hooks
        except ImportError as err:
            for arg in err.args:
                print('Cannot import hooks from %s: %s' % (conf_dir, arg))
        self.rules = rules

