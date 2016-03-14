import gdsync.cli.backup
from gdsync.cli.backup import Backup
from gdsync.config import Config


class TestBackupTest:
    def test_init(self):
        backup = Backup()
        assert isinstance(backup.backup, gdsync.google.backup.Backup)
        assert '_print' == backup.backup.callback.__name__
        assert isinstance(backup.config, Config)
