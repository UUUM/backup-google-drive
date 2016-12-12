import httplib2
import io
import os
import simplejson
import six

from apiclient import discovery
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
import oauth2client
from oauth2client import client, tools

import gdsync

DEFAULT_RESOURCE_FIELDS = ','.join([
    'id',
    'capabilities',
    'createdTime',
    'mimeType',
    'modifiedTime',
    'name',
    'parents',
    'trashed',
])
MIME_TYPE_APP = 'application/vnd.google-apps.drive-sdk'
MIME_TYPE_FOLDER = 'application/vnd.google-apps.folder'
MIME_TYPE_MAP = 'application/vnd.google-apps.map'


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
        return self._call_api('add_parents', file, parents)

    def copy(self, file, parents=None):
        if not file.capabilities['canCopy']:
            return False
        return self._call_api('copy', file, parents=parents)

    def create(self, name, content=None, media_body=None, mime_type=None, parents=None):
        return self._call_api(
            'create',
            name,
            content=content,
            media_body=media_body,
            mime_type=mime_type,
            parents=parents
        )

    def create_folder(self, name, parents=None):
        return self.create(name, mime_type=MIME_TYPE_FOLDER, parents=parents)

    @property
    def credentials(self):
        if not self._credentials:
            self._credentials = self._create_credentials()
        return self._credentials

    def delete(self, file):
        return self._call_api('delete', file)

    def get(self, file):
        return self._call_api('get', file)

    @property
    def http(self):
        if not self._http:
            self._http = self._create_http()
        return self._http

    def list(self, query=None, order_by=None, page_size=1000):
        page_token = None
        while True:
            files, page_token = self._call_api(
                'list',
                query=query,
                order_by=order_by,
                page_size=page_size,
                page_token=page_token
            )
            for file in files:
                res = Resource(self, file['id'])
                for key in file:
                    setattr(res, key, file[key])
                yield res

            if page_token is None:
                break

    def open(self, id):
        return Resource(self, id)

    def remove_parents(self, file, parents):
        return self._call_api('remove_parents', file, parents)

    @property
    def service(self):
        if not self._service:
            Drive._service = self._create_service()
        return self._service

    def _api_add_parents(self, file, parents):
        self.service.files().update(
            fileId=file.id,
            addParents=self._create_parents_str(parents),
        ).execute()

        return self

    def _api_copy(self, file, parents=None):
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

    def _api_create(self, name, content=None, media_body=None, mime_type=None, parents=None):
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

    def _api_delete(self, file):
        self.service.files().delete(
            fileId=file.id,
        ).execute()

        return self

    def _api_get(self, file):
        return self.service.files().get(
            fileId=file.id,
            fields=DEFAULT_RESOURCE_FIELDS,
        ).execute()

    def _api_list(self, query=None, order_by=None, page_size=1000, page_token=None):
        fields = 'nextPageToken, files(%s)' % DEFAULT_RESOURCE_FIELDS
        response = self.service.files().list(
            q=query,
            spaces='drive',
            fields=fields,
            orderBy=order_by,
            pageToken=page_token,
            pageSize=page_size,
        ).execute()

        return (response.get('files', []), response.get('nextPageToken', None))

    def _api_remove_parents(self, file, parents):
        self.service.files().update(
            fileId=file.id,
            removeParents=self._create_parents_str(parents),
        ).execute()

        return self

    def _call_api(self, method_name, *args, **kwargs):
        try:
            method = getattr(self, '_api_{}'.format(method_name))
            return method(*args, **kwargs)
        except HttpError as error:
            error = self._create_error(error)
            error.method = method_name
            error.method_args = args
            error.method_kwargs = kwargs
            raise error

    def _create_credentials(self):
        store = oauth2client.file.Storage(self.credential_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            import argparse
            flags = argparse.ArgumentParser(
                parents=[tools.argparser]
            ).parse_args([])
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
    method_args = []
    method_kwargs = {}

    _contents = None

    @property
    def contents(self):
        if not self._contents:
            self._contents = simplejson.loads(self.content)
        return self._contents

    def is_reason(self, reason):
        for error in self.contents['error']['errors']:
            if error['reason'] == reason:
                return True
        return False


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
