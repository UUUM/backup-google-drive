# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import pytest

import gdsync
from gdsync.google.drive import Drive

TEST_FOLDER_NAME = 'gdsync-test'


@pytest.fixture()
def delete_db_file(request, sqlite_file):
    def fin():
        if os.path.isfile(sqlite_file):
            os.unlink(sqlite_file)
    request.addfinalizer(fin)
    fin()


@pytest.fixture()
def sqlite_file(request):
    return os.path.join(gdsync.VAR_DIR, 'test.db')


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
