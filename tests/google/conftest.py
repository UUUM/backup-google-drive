import os

import pytest

from gdsync.google.drive import Drive
from gdsync.google.finished_folders import FinishedFolders

TEST_FOLDER_NAME = 'gdsync-test'


@pytest.fixture()
def delete_db_file(request):
    def fin():
        file = FinishedFolders('xxxxxx').db_file
        if os.path.isfile(file):
            os.unlink(file)
    request.addfinalizer(fin)
    fin()


@pytest.fixture(scope='session')
def test_folder(request):
    def fin():
        res.delete()
    request.addfinalizer(fin)

    res = Drive().create_folder(TEST_FOLDER_NAME)
    return res


@pytest.fixture(scope='session')
def dest_folder(request, test_folder):
    def fin():
        res.delete()
    request.addfinalizer(fin)

    res = test_folder.create_folder('バックアップ先')
    return res


@pytest.fixture(scope='session')
def src_folder(request, test_folder):
    def fin():
        res.delete()
    request.addfinalizer(fin)

    res = test_folder.create_folder('バックアップ元')
    sub_folder = res.create_folder('フォルダ')
    sub_folder.create('テストsub', content='test')
    return res


@pytest.fixture(scope='session')
def src_file(request, src_folder):
    def fin():
        for file in files:
            file.delete()
    request.addfinalizer(fin)

    files = []
    files.append(src_folder.create('テスト', content='test'))
    files.append(src_folder.create('テスト', content='foo,bar', mime_type='text/csv'))
    return files[0]
