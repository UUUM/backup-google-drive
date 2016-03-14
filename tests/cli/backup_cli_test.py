import gdsync.cli.backup
from gdsync.cli.backup import Sync
from gdsync.config import Config


class TestSyncTest:
    def test_init(self):
        backup = Sync()
        assert isinstance(backup.backup, gdsync.google.sync.Sync)
        assert '_print' == backup.backup.callback.__name__
        assert isinstance(backup.config, Config)
