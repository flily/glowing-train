#!/usr/bin/python


import logging
import json
import bz2
import gzip
import MySQLdb

import hascrpt


class Locomotive(object):
    def __init__(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
        self.mysql.autocommit(True)
        self.cursor = self.mysql.cursor()
        self.field_map = {}
        self.sys_conf = {}

    def connect_db(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
        self.mysql.autocommit(True)
        self.cursor = self.mysql.cursor()

    def load_map(self, field_map):
        self.field_map = field_map

    def load_sys_conf(self, sys_conf):
        self.sys_conf = sys_conf

    def get_table_rows(self, table_name):
        try:
            sql = "SELECT COUNT(*) FROM `%s`" % table_name
            self.cursor.execute(sql)
            return self.cursor.fetchall()[0][0]

        except MySQLdb.ProgrammingError as ex:
            logging.debug("Programming Error: %s", ex)
            return None

    def get_table_columns_name(self, table_name):
        try:
            sql = "SHOW columns FROM `%s`" % table_name
            self.cursor.execute(sql)
            columns_info = self.cursor.fetchall()
            return [x[0] for x in columns_info]

        except MySQLdb.ProgrammingError as ex:
            logging.debug("Programming Error: %s", ex)
            return None

    def select_table_range(self, table_name, offset, count):
        sql = "SELECT * FROM `%s` LIMIT %s, %s" % (table_name, offset, count)

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def open_target_file(self, filename, format="plain"):
        if format in ["gzip", "gz"]:
            return gzip.open(filename + ".gz", "w")

        elif format in ["bzip2", "bz2"]:
            return bz2.BZ2File(filename + ".bz2", "w")

        else:
            return open(filename, "w")

    def dump_table(self, filename, table_name, count):
        rows_num = self.get_table_rows(table_name)
        offset = 0
        dump_count = 0

        if rows_num is None:
            logging.error("Table '%s' not found", table_name)
            return

        column_names = self.get_table_columns_name(table_name)
        column_map = dict(zip(column_names, range(0, len(column_names))))

        hash_method = self.sys_conf.get("hash_method", "sha1")
        email_key = self.sys_conf.get("email_key", "email")
        password_key = self.sys_conf.get("password_key", "password")
        output_format = self.sys_conf.get("format", "bzip2")
        lower_email_only = self.sys_conf.get("lower_email", "yes") == "yes"

        with self.open_target_file(filename, output_format) as fp:
            while offset < rows_num:
                result = self.select_table_range(table_name, offset, count)
                for row in result:
                    try:
                        email = row[column_map[email_key]]
                        password = row[column_map[password_key]]
                        if lower_email_only:
                            email = email.lower()

                        logging.debug("%s  %s %s", list(row), email, password)

                        content = hascrpt.hash_info(hash_method,
                                                    email=email, password=password)
                        logging.debug("Content: %s", content)
                        fp.write(json.dumps(content) + "\n")
                        dump_count += 1

                    except Exception as ex:
                        logging.error("ERROR FOR DATA: %s", ex)
                        logging.error("ERROR DATA: %s", row)

                offset += len(result)
                logging.info("%s of %s/%s records dump",dump_count, offset, rows_num)

