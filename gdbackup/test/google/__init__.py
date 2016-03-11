import os
import unittest

from gdbackup.google.drive import Drive, Resource
from gdbackup.google.finished_folders import FinishedFolders

TEST_FOLDER_NAME = 'backup-google-drive-test'


class TestCase(unittest.TestCase):
    test_folder = None
    dest_folder = None
    src_folder = None

    @classmethod
    def _create_test_folder(cls):
        cls.test_folder = Drive().create_folder(TEST_FOLDER_NAME)

        cls.dest_folder = cls.test_folder.create_folder('バックアップ先')

        cls.src_folder = cls.test_folder.create_folder('バックアップ元')
        cls.src_file = cls.src_folder.create('テスト', content='test')
        cls.src_folder.create('テスト', content='foo,bar', mime_type='text/csv')

        sub_folder = cls.src_folder.create_folder('フォルダ')
        sub_folder.create('テストsub', content='test')

    @classmethod
    def _delete_test_folder(cls):
        if cls.test_folder:
            cls.test_folder.delete()

    def _remove_db_file(self):
        file = FinishedFolders('xxxxxx').db_file
        if os.path.isfile(file):
            os.unlink(file)
