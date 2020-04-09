import os
import yaml
import logging


## get value from HOME/lab/mlsteam.yml
def get_value(key, default=None):
    _dir = os.getenv('HOME', None)
    if not _dir:
        logging.warning("use default value for {}, HOME environment variable undefined.".format(key))
        return default
    param_file = os.path.join(_dir, "lab", "mlsteam.yml")
    if not os.path.exists(param_file):
        logging.warning("use default value for {}, mlsteam.yml not found.".format(key))
        return default
    params = {}
    with open(param_file, 'r') as f:
        params = yaml.safe_load(f)
    if "params" not in params:
        logging.warning("use default value for {}, undefined variable.".format(key))
        return default

    if key in params['params']:
        values = None
        if isinstance(params['params'][key], dict):
            values = params['params'][key]['values']
        else:
            values = params['params'][key]

        if isinstance(values, list):
            logging.warning("key {} is a list, use first value {}".format(key, values[0]))
            return values[0]
        logging.info("use {}: {}".format(key, values))
        return values

        logging.warning("use default value for {}, undefined variable.".format(key))
    return default