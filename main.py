#!/usr/bin/python


import sys
import logging
import yaml

from Locomotive import Locomotive


DEFAULT_CONF_FILE = "train.conf.yaml"


def load_conf(filename):
    with open(filename) as fp:
        content = fp.read()
        return yaml.load(content)


def get_log_format(fmt=""):
    if fmt:
        return logging.Formatter(fmt)

    f = "[%(asctime)s] %(levelname)s: %(message)s"
    if not isinstance(sys.version_info, tuple):
        f = "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d: %(message)s"

    return logging.Formatter(f)


def init_logger(filename_base, have_console=True):
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    if have_console:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(get_log_format("[%(asctime)s] %(message)s"))
        logger.addHandler(console)

    output = logging.FileHandler("%s.log" % filename_base)
    output.setLevel(logging.INFO)
    output.setFormatter(get_log_format())
    logger.addHandler(output)

    debug = logging.FileHandler("%s.debug.log" % filename_base)
    debug.setLevel(logging.DEBUG)
    debug.setFormatter(get_log_format())
    logger.addHandler(debug)


def main():
    init_logger("train")
    conf = load_conf(DEFAULT_CONF_FILE)

    loco = Locomotive()
    loco.connect(**conf["db"])


if __name__ == "__main__":
    main()

