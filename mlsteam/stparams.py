import os
import click
import logging
import yaml

filename = 'mlsteam.yml'
HOME = os.getenv('HOME', '/')

# PWD/mlsteam.yml
# HOME/mlsteam.yml
# HOME/lab/mlsteam.yml


def get_value(key, default=None):
    dirs = [os.getcwd(), HOME, os.path.join(HOME, 'lab')]
    param_file = ""
    for _dir in dirs:
        file_lookup = os.path.join(_dir, filename)
        if os.path.exists(file_lookup):
            param_file = file_lookup
            break

    if not param_file:
        logging.warning(
            "use default value for {}, mlsteam.yml not found.".format(key))
        return default

    params = {}
    with open(param_file, encoding='utf-8', mode='r') as f:
        params = yaml.safe_load(f)
    if params is None or "params" not in params:
        logging.warning(
            "use default value for {}, undefined variable.".format(key))
        return default
    for k, v in params["params"].iteritems():
        if key == k:
            if isinstance(params["params"][key], list):
                click.echo("hyperparameter - {}: {}".format(key,
                           params["params"][key][0]))
                return params["params"][key][0]
            click.echo(
                "hyperparameter - {}: {}".format(key, params["params"][key]))
            return params["params"][key]
    click.echo("hyperparameter - {}: {}(default)".format(key, default))
    return default
