# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import httplib2
import unittest

import oauth2client
import googleapiclient

from gdbackup.google.drive import Drive, Resource
from gdbackup.test.google import TestCase


class DriveTest(TestCase):
    def test_create(self):
        drive = Drive()

        file = drive.create('test.txt', content='test')
        file = drive.open(file.id)
        assert 'test.txt' == file.name
        assert 'text/plain' == file.mimeType

        drive.delete(file)

    def test_create_folder(self):
        drive = Drive()

        folder = drive.create_folder('テストフォルダ')
        res = Resource(drive, folder.id)
        assert isinstance(folder, Resource)
        assert folder.id == res.id
        assert 'テストフォルダ' == res.name
        assert 'application/vnd.google-apps.folder' == res.mimeType

        drive.delete(folder)

    def test_credential(self):
        drive = Drive()

        credentials = drive.credentials
        assert isinstance(credentials, oauth2client.client.OAuth2Credentials)
        assert id(credentials) == id(drive.credentials)

    def test_http(self):
        drive = Drive()

        http = drive.http
        assert isinstance(http, httplib2.Http)
        assert id(http) == id(drive.http)

    def test_list(self):
        drive = Drive()
        i = 0
        for file in drive.list(page_size=1):
            i += 1
            if 2 <= i:
                break
        assert 2 <= i

    def test_open(self):
        drive = Drive()

        res = drive.open('xxxxxx')
        assert isinstance(res, Resource)
        assert res.id == 'xxxxxx'

    def test_service(self):
        drive = Drive()

        service = drive.service
        assert isinstance(service, googleapiclient.discovery.Resource)
        assert id(service) == id(drive.service)


class ResourceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._create_test_folder()

    @classmethod
    def tearDownClass(cls):
        cls._delete_test_folder()

    def test_init(self):
        drive = Drive()

        res = Resource(drive, 'xxxxxx')
        assert isinstance(res, Resource)
        assert id(drive) == id(res.drive)
        assert 'xxxxxx' == res.id

        try:
            Resource(drive, 0)
        except ValueError:
            pass
        else:
            assert False, 'should receive ValueError exception'

    def test_metadata(self):
        res = Resource(Drive(), self.dest_folder.id)
        metadata = res.metadata
        assert 'id' in metadata
        assert 'mimeType' in metadata
        assert 'name' in metadata
        assert id(metadata) == id(res.metadata)

    def test_metadata_property(self):
        res = Resource(Drive(), self.dest_folder.id)
        res.name = '名前テスト'
        assert '名前テスト' == res.name

        res = Resource(Drive(), self.dest_folder.id)
        assert 'バックアップ先' == res.name

    def test_add_remove(self):
        src_res = Resource(Drive(), self.src_file.id)
        dest_res = Resource(Drive(), self.dest_folder.id)

        file = src_res.copy_to(dest_res)
        folder = dest_res.create_folder('folder')
        file.add_to(folder)
        assert dest_res.id in file.parents
        assert folder.id in file.parents

        file.remove_from(folder)
        file = Resource(Drive(), file.id)
        assert dest_res.id in file.parents
        assert folder.id not in file.parents

    def test_copy_to(self):
        src_res = Resource(Drive(), self.src_file.id)
        dest_res = Resource(Drive(), self.dest_folder.id)

        res = src_res.copy_to(dest_res)
        res = Resource(Drive(), res.id)
        assert src_res.id != res.id
        assert src_res.name == res.name
        assert src_res.parents[0] != res.parents[0]
        res.delete()

    def test_create(self):
        res = Resource(Drive(), self.dest_folder.id)
        folder = res.create('test.txt', content='test')

        res = Resource(Drive(), folder.id)
        assert folder.id == res.id
        assert 'test.txt' == res.name
        assert 'text/plain' == res.mimeType
        assert res.parents[0] == self.dest_folder.id
        res.delete()

    def test_create_folder(self):
        res = Resource(Drive(), self.dest_folder.id)
        folder = res.create_folder('テストフォルダ')

        res = Resource(Drive(), folder.id)
        assert folder.id == res.id
        assert 'テストフォルダ' == res.name
        assert 'application/vnd.google-apps.folder' == res.mimeType
        assert res.parents[0] == self.dest_folder.id
        res.delete()

    def test_delete(self):
        res = Resource(Drive(), self.dest_folder.id)
        folder = res.create_folder('テストフォルダ')
        assert not folder.trashed

        # 削除したファイルのデータはとれなくなる
        folder.delete()
        try:
            Resource(Drive(), folder.id).metadata
        except googleapiclient.errors.HttpError as e:
            assert e.resp['status'] == '404'
        else:
            assert False, 'should receive googleapiclient.errors.HttpError exception'

    def test_find(self):
        res = Resource(Drive(), self.src_folder.id)

        assert res.find('ダミー名') is None

        assert isinstance(res.find('テスト'), Resource)
        assert isinstance(res.find('テスト', mime_type='text/plain'), Resource)
        assert isinstance(res.find('テスト', mime_type='text/csv'), Resource)
        assert res.find('テスト', mime_type='image/jpeg') is None

    def test_find_folder(self):
        res = Resource(Drive(), self.src_folder.id)
        assert isinstance(res.find_folder('フォルダ'), Resource)
        assert res.find_folder('テスト') is None
        assert res.find_folder('ダミー名') is None

    def test_has(self):
        res = Resource(Drive(), self.src_folder.id)

        assert not res.has('ダミー名')

        assert res.has('テスト')
        assert res.has('テスト', mime_type='text/plain')
        assert res.has('テスト', mime_type='text/csv')
        assert not res.has('テスト', mime_type='image/jpg')

    def test_has_folder(self):
        res = Resource(Drive(), self.src_folder.id)
        assert res.has_folder('フォルダ')
        assert not res.has_folder('テスト')
        assert not res.has_folder('ダミー名')

    def test_is_folder(self):
        res = Resource(Drive(), self.dest_folder.id)
        assert res.is_folder()

        res = Resource(Drive(), self.src_file.id)
        assert not res.is_folder()

    def test_list(self):
        # page_size を 1 にして、ページ送りがあってもちゃんと取得できるか
        res = Resource(Drive(), self.src_folder.id)
        i = 0
        for file in res.list(page_size=1):
            i += 1
        assert 2 <= i

    def test_list_all(self):
        res = Resource(Drive(), self.src_folder.id)
        files = res.list_all(page_size=1)
        assert 'テスト' in files
        assert isinstance(files['テスト'], dict)
        assert 2 == len(files['テスト'])
        for file in files['テスト'].values():
            assert file.mimeType in ('text/plain', 'text/csv')


if __name__ == '__main__':
    unittest.main()