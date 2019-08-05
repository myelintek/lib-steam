import json
import click
from datetime import datetime
from api import MyelindlApi, MyelindlApiError

@click.command()
@click.argument('id', required=True)
def download(id):
    try:
        api = MyelindlApi()
        result = api.checkpoint_download(id)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo("download checkpoint failed, {}".format(e))
        raise


@click.command()
def list():
    try:
        api = MyelindlApi()
        result = api.checkpoint_list()
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("list checkpoint failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def delete(id):
    try:
        api = MyelindlApi()
        result = api.checkpoint_delete(id)
    except MyelindlApiError as e:
        click.echo("delete a checkpoint failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def info(id):
    try:
        api = MyelindlApi()
        result=api.checkpoint_info(id)
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("show checkpoint info failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage checkpoints')
def checkpoint():
    pass


checkpoint.add_command(download)
checkpoint.add_command(list)
checkpoint.add_command(delete)
checkpoint.add_command(info)
