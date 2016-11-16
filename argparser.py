default_conf_path = '/home/juraj/Documents/mYstable/config/medusa.conf'


def open_default_conf_file():
    config_file = open(default_conf_path, mode='r')
    return config_file


def open_config_file(args):
    if args.config:  # prepinac -c bol zadany
        try:
            config_file = open(args.config, mode='r')
            print("Config file: " + config_file.name + " opened.")
        except IOError:
            config_file = open_default_conf_file()
            print("Config file was not found. Default file used: " + config_file.name)

    else:  # prepinac -c nebol zadany, pouzi defualt cestu k suboru
        config_file = open_default_conf_file()
        print("Default config file used: " + config_file.name)

    return config_file
