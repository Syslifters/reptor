import os

import yaml

config_path = os.path.join(os.path.expanduser("~"), ".sysreptor/config.yaml")


def load_config():
    config = dict()
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f.read())
    except FileNotFoundError:
        pass
    return config


config = load_config()


def get_config_from_user():
    config = load_config()

    default_server = config.get('server', 'https://demo.sysre.pt')
    config['server'] = input(
        f"Server [{default_server}]: ") or default_server
    default_api_token = config.get('token')
    config['token'] = input(f"API Token{ f' [{default_api_token}]' if default_api_token else ''}: ") \
        or config.get('token')
    default_project_id = config.get('project_id')
    config['project_id'] = input(f"Project ID{ f' [{default_project_id}]' if default_project_id else ''}: ") \
        or default_project_id
    store_config(config)


def store_config(config):
    store = None
    while store not in ['y', 'n']:
        store = input("Store to config to ~/.sysreptor/config.yaml? [y/n]: ")
    if store == 'y':
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
