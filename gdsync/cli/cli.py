import os
from pprint import pprint

import click
from googleapiclient.errors import HttpError

from gdsync.google.sync import Sync


class Cli:
    def main(self):
        try:
            self._sync()
        except HttpError as error:
            self._error(error)

    def _sync(self):
        Sync(
            self.source,
            self.destination,
            callback=self._print,
            config_dir=self.config_dir,
            sqlite_file=self.sqlite_file,
            sync_id=self.sync_id,
        ).sync()

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
@click.option(
    '--config-dir',
    default=os.path.join(os.path.expanduser('~'), '.gdsync'),
    help='config directory',
)
@click.option('--sqlite-file', help='sqlite file to store information of progress')
@click.option('--sync-id', help='unique id for syncronization')
def main(source, destination, config_dir, sqlite_file, sync_id):
    cli = Cli()

    cli.source = source
    cli.destination = destination
    cli.config_dir = config_dir
    cli.sqlite_file = sqlite_file
    cli.sync_id = sync_id

    cli.main()


if __name__ == "__main__":
    main()
