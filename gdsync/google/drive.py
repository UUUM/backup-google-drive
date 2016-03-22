import httplib2
import io
import os
import six

from apiclient import discovery
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
import oauth2client
from oauth2client import client, tools

import gdsync

DEFAULT_RESOURCE_FIELDS = 'id, createdTime, mimeType, modifiedTime, name, parents, trashed'
MIME_TYPE_APP = 'application/vnd.google-apps.drive-sdk'
MIME_TYPE_FOLDER = 'application/vnd.google-apps.folder'


class Drive:
    SCOPES = 'https://www.googleapis.com/auth/drive'

    _credentials = None
    _http = None
    _service = None

    def __init__(self, config_dir=None):
        if config_dir:
            self.config_dir = config_dir
        else:
            self.config_dir = gdsync.CONFIG_DIR

        self.client_secret_file = os.path.join(self.config_dir, 'client_secrets.json')
        self.credential_file = os.path.join(self.config_dir, 'credentials.json')

    def add_parents(self, file, parents):
        try:
            self.service.files().update(
                fileId=file.id,
                addParents=self._create_parents_str(parents),
            ).execute()

            return self
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'add_parents'
            error.method_args = {
                'file': file,
                'parents': parents,
            }
            raise error

    def copy(self, file, parents=None):
        try:
            metadata = {
                'name': file.name,
                'parents': self._create_parents_list(parents),
            }
            response = self.service.files().copy(
                fileId=file.id,
                body=metadata,
            ).execute()

            res = Resource(self, response['id'])
            for key in response:
                setattr(res, key, response[key])

            return res
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'copy'
            error.method_args = {
                'file': file,
                'parents': parents,
            }
            raise error

    def create(self, name, content=None, media_body=None, mime_type=None, parents=None):
        try:
            if content is not None:
                if isinstance(content, six.string_types):
                    if mime_type is None:
                        mime_type = 'text/plain'
                    fd = io.BytesIO(bytearray(content, 'utf8'))
                elif isinstance(content, six.binary_type):
                    fd = io.BytesIO(content)
                else:
                    raise ValueError('content must be string or binary')

                media_body = MediaIoBaseUpload(
                    fd,
                    mimetype=mime_type,
                    resumable=True,
                )

            metadata = {
                'name': name,
                'mimeType': mime_type,
                'parents': self._create_parents_list(parents),
            }
            folder = self.service.files().create(
                body=metadata,
                fields=DEFAULT_RESOURCE_FIELDS,
                media_body=media_body,
            ).execute()

            res = Resource(self, folder['id'])
            for key in folder:
                setattr(res, key, folder[key])
            res._files = {}

            return res
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'create'
            error.method_args = {
                'name': name,
                'mime_type': mime_type,
                'parents': parents,
            }
            raise error

    def create_folder(self, name, parents=None):
        return self.create(name, mime_type=MIME_TYPE_FOLDER, parents=parents)

    @property
    def credentials(self):
        if not self._credentials:
            self._credentials = self._create_credentials()
        return self._credentials

    def delete(self, file):
        try:
            self.service.files().delete(
                fileId=file.id,
            ).execute()

            return self
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'delete'
            error.method_args = {
                'file': file,
            }
            raise error

    def get(self, file):
        try:
            return self.service.files().get(
                fileId=file.id,
                fields=DEFAULT_RESOURCE_FIELDS,
            ).execute()
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'get'
            error.method_args = {
                'file': file,
            }
            raise error

    @property
    def http(self):
        if not self._http:
            self._http = self._create_http()
        return self._http

    def list(self, order_by=None, page_size=1000, query=None):
        try:
            page_token = None
            while True:
                fields = 'nextPageToken, files(%s)' % DEFAULT_RESOURCE_FIELDS
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields=fields,
                    orderBy=order_by,
                    pageToken=page_token,
                    pageSize=page_size,
                ).execute()

                for file in response.get('files', []):
                    res = Resource(self, file['id'])
                    for key in file:
                        setattr(res, key, file[key])
                    yield res

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'list'
            error.method_args = {
                'file': file,
            }
            raise error

    def open(self, id):
        return Resource(self, id)

    def remove_parents(self, file, parents):
        try:
            self.service.files().update(
                fileId=file.id,
                removeParents=self._create_parents_str(parents),
            ).execute()

            return self
        except HttpError as error:
            error = self._create_error(error)
            error.method = 'remove_parents'
            error.method_args = {
                'file': file,
                'parents': parents,
            }
            raise error

    @property
    def service(self):
        if not self._service:
            Drive._service = self._create_service()
        return self._service

    def _create_credentials(self):
        store = oauth2client.file.Storage(self.credential_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            import argparse
            flags = argparse.ArgumentParser(
                parents=[tools.argparser]
            ).parse_args()
            flow = client.flow_from_clientsecrets(
                self.client_secret_file,
                self.SCOPES
            )
            credentials = tools.run_flow(flow, store, flags)
        return credentials

    def _create_error(self, error):
        new_error = DriveError(error.resp, error.content)
        new_error.__dict__ = error.__dict__.copy()
        return new_error

    def _create_http(self):
        return self.credentials.authorize(httplib2.Http())

    def _create_parents_list(self, parents):
        if parents is None:
            return []

        if isinstance(parents, Resource):
            return [parents.id]

        param = []
        for parent in parents:
            param.append(parent.id)
        return param

    def _create_parents_str(self, parents):
        return ','.join(self._create_parents_list(parents))

    def _create_service(self):
        return discovery.build('drive', 'v3', http=self.http)


class DriveError(HttpError):
    method = None
    method_args = {}


class Resource:
    _files = None

    def __init__(self, drive, id):
        if not isinstance(id, six.string_types):
            raise ValueError('Google Drive File ID must be a string')

        self.drive = drive
        self.id = id

    def __getattr__(self, name):
        if name == 'metadata':
            value = self._get_metadata()
        else:
            metadata = self.metadata
            if name not in metadata:
                raise AttributeError
            value = metadata[name]

        setattr(self, name, value)
        return value

    def add_to(self, res):
        self.drive.add_parents(self, res)
        return self

    def copy_to(self, res):
        return self.drive.copy(self, parents=[res])

    def create(self, name, content=None, mime_type=None):
        return self.drive.create(name, content=content, mime_type=mime_type, parents=[self])

    def create_folder(self, name, unique=True):
        if unique:
            folder = self.find_folder(name)
            if folder:
                return folder

        return self.drive.create_folder(name, parents=[self])

    def delete(self):
        self.drive.delete(self)
        return self

    def files(self):
        if not self._files:
            self._files = self.list_all()
        return self._files

    def find(self, name, mime_type=None):
        files = self.files()

        if name not in files:
            return None

        if not mime_type:
            return list(files[name].values())[0]

        for file in files[name].values():
            if file.mimeType == mime_type:
                return file

        return None

    def find_folder(self, name):
        return self.find(name, mime_type=MIME_TYPE_FOLDER)

    def has(self, name, mime_type=None):
        return self.find(name, mime_type) is not None

    def has_folder(self, name):
        return self.has(name, mime_type=MIME_TYPE_FOLDER)

    def is_app(self):
        return self.mimeType.startswith(MIME_TYPE_APP)

    def is_folder(self):
        return self.mimeType == MIME_TYPE_FOLDER

    def list(self, order_by=None, page_size=1000):
        query = "'%s' in parents and trashed = false" % self.id
        return self.drive.list(order_by=order_by, page_size=page_size, query=query)

    def list_all(self, page_size=1000):
        list = {}
        for file in self.list(page_size=page_size):
            name = file.name
            if name not in list:
                list[name] = {}
            list[name][file.id] = file
        self._files = list
        return list

    def remove_from(self, res):
        self.drive.remove_parents(self, res)
        return self

    def _get_metadata(self):
        return self.drive.get(self)
