import os
from pprint import pprint

import click
from googleapiclient.errors import HttpError

import gdsync.google.sync


class Cli:
    def main(self, src, dest):
        try:
            self._sync(src, dest)
        except HttpError as error:
            self._error(error)

    def _sync(self, src, dest):
        sync = gdsync.google.sync.Sync(src, dest)
        sync.callback = self._print
        sync.sync()

    def _error(self, error):
        print(error.uri)
        pprint(error.resp)
        raise error

    def _print(self, src_item, folder_name, state=''):
        name = os.path.join(folder_name, src_item.name)
        if src_item.is_folder():
            name += '/'

        print('%s: %s' % (state, name))


@click.command()
@click.argument('source')
@click.argument('destination')
def main(source, destination):
    Cli().main(source, destination)


if __name__ == "__main__":
    main()
