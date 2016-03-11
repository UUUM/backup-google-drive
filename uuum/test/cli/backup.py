import unittest

import uuum.cli.backup
from uuum.cli.backup import Backup
from uuum.config import Config


class BackupTest(unittest.TestCase):
    def test_init(self):
        backup = Backup()
        assert isinstance(backup.backup, uuum.google.backup.Backup)
        assert '_print' == backup.backup.callback.__name__
        assert isinstance(backup.config, Config)


if __name__ == '__main__':
    unittest.main()
