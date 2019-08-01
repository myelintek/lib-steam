import json
import click
from datetime import datetime
from api import MyelindlApi, MyelindlApiError

@click.command()
@click.argument('id', required=True)
def create(id):
    try:
        api = MyelindlApi()
        result = api.service_create(id)
        click.echo(result)
    except MyelindlApiError, e:
        click.echo("create service failed, {}".format(e))
        raise


@click.command()
def list():
    try:
        api = MyelindlApi()
        result = api.service_list()
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError, e:
        click.echo("list service failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def delete(id):
    try:
        api = MyelindlApi()
        result = api.service_delete(id)
    except MyelindlApiError, e:
        click.echo("delete a service failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage services')
def service():
    pass


service.add_command(create)
service.add_command(list)
service.add_command(delete)
