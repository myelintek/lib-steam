import os
import yaml
import logging


## get value from JOB_DIR/param.yml
def get_value(key, default=None):
    _dir = os.getenv('JOB_DIR', None)
    if not _dir:
        logging.warning("use default value for {}, JOB_DIR environment variable undefined.".format(key))
        return default
    param_file = os.path.join(_dir, "param.yml")
    if not os.path.exists(param_file):
        logging.warning("use default value for {}, param.yml not found.".format(key))
        return default
    params = {}
    with open(param_file, 'r') as f:
        params = yaml.safe_load(f)
    for k, v in params.iteritems():
        if key == k:
            logging.info("use {}: {}".format(k, v))
            return params[key]
    logging.warning("use default value for {}, undefined variable.".format(key))
    return default
