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


def main(args):
    init_logger("train")
    conf = load_conf(DEFAULT_CONF_FILE)

    loco = Locomotive(**conf["db"])

    if len(args) < 2:
        logging.error("No argument found")
        return

    action = args[0].lower()
    if "count" == action:
        table_name = args[1]
        count = loco.get_table_rows(table_name)
        if count is None:
            logging.info("Table '%s' not found or broken", table_name)
        else:
            logging.info("Rows of '%s': %s", table_name, count)

    elif "list" == action:
        table_name = args[1]
        each_count = 1000
        if len(args) > 2:
            each_count = int(args[2])

        loco.dump_table(table_name, each_count)


if __name__ == "__main__":
    main(sys.argv[1:])

