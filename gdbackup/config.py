import os

import yaml

import gdbackup

CONFIG_FILE = os.path.join(gdbackup.CONFIG_DIR, 'config.yml')


class Config(dict):
    def __init__(self, config_file=None):
        if not config_file:
            config_file = CONFIG_FILE
        with open(config_file) as fd:
            self.update(yaml.load(fd))
