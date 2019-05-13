import os
import click
from api import MyelindlApi, MyelindlApiError
from mlsteam import version

@click.command()
def info():
    try:
        api = MyelindlApi()
        server_ver = api.version()
        click.echo("Version: {}, sha: {}".format(version.__version__, version.__sha__))
        click.echo("Server: {}".format(api.host))
        click.echo("Username: {}".format(api.username))
        click.echo("Data Port: {}".format(self.data_port))
    except MyelindlApiError as e:
        click.echo(u'Fail due to {}'.format(e))

