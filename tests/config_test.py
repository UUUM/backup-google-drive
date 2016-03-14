import os

import gdsync
from gdsync.config import Config

gdsync.config.CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.yml')


class TestConfig:
    def test_init(self):
        config = Config()
        assert 'sync' in config
        assert 'source_ids' in config['sync']
        assert 'destination_id' in config['sync']
