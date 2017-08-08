from constants import MED_OK, MED_NO
from importlib import import_module

class Conf():
    confs = {}
    def load(host):
        conf_dir = host['host_confdir']
        if conf_dir in Conf.confs:
            return Conf.confs[conf_dir]
        conf = Conf(host)
        Conf.confs[conf_dir] = conf

        return conf
        
    def __init__(self, host): 
        conf_dir = host['host_confdir']

        configuration = None
        try:
            conf = import_module(conf_dir.replace('/', '.'), package=None)
            #conf.__dict__['__name__'] = host['host_name']
            conf.__dict__['hostname'] = host['host_name']
            configuration = conf.conf
        except ImportError as err:
            for arg in err.args:
                print('Cannot import hooks from %s: %s' % (conf_dir, arg))
        self.conf = configuration

