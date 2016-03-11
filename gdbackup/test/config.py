import os
import unittest

import gdbackup.config
from gdbackup.config import Config

gdbackup.config.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.yml')


class ConfigTest(unittest.TestCase):
    def test_init(self):
        config = Config()
        assert 'sync' in config
        assert 'source_ids' in config['sync']
        assert 'destination_id' in config['sync']


if __name__ == '__main__':
    unittest.main()