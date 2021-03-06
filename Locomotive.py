#!/usr/bin/python


import datetime
import logging
import json
import bz2
import gzip
import MySQLdb

import hascrpt
import checker


def _email_map_hook(email):
    return email


def _password_map_hook(password):
    return password


def _phone_map_hook(phone):
    return phone


def _username_map_hook(username):
    try:
        if not username:
            return None

        return username.decode("utf8")

    except UnicodeDecodeError:
        return None


def _content_final_hook(content):
    o = {}
    for key in content:
        if content[key]:
            o[key] = content[key]

    return o


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

    def overload_sys_conf(self, name, value):
        self.sys_conf[name] = value

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

    def select_table_range(self, table_name, offset, count, by_id="uid"):
        sql = "SELECT * FROM `%s` LIMIT %s, %s" % (table_name, offset, count)
        if by_id and by_id.lower() not in ["null", "none", "nil"]:
            lower_bound = offset
            upper_bound = offset + count
            sql = "SELECT * FROM `%s` WHERE `%s` >= %s and `%s` < %s" \
                  % (table_name, by_id, lower_bound, by_id, upper_bound)

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def open_target_file(self, filename, format="plain"):
        if format in ["gzip", "gz"]:
            return gzip.open(filename + ".gz", "w")

        elif format in ["bzip2", "bz2"]:
            return bz2.BZ2File(filename + ".bz2", "w")

        else:
            return open(filename, "w")

    def dump_table(self, filename, table_name):
        rows_num = self.get_table_rows(table_name)
        offset = 0
        dump_count = 0

        if rows_num is None:
            logging.error("Table '%s' not found", table_name)
            return

        column_names = self.get_table_columns_name(table_name)
        column_map = dict(zip(column_names, range(0, len(column_names))))

        each_count = self.sys_conf.get("each_count", 2000)
        hash_method = self.sys_conf.get("hash_method", "sha1")
        email_key = self.sys_conf.get("email_key", "email")
        phone_key = self.sys_conf.get("phone_key", "qq")
        username_key = self.sys_conf.get("username_key", "username")
        password_key = self.sys_conf.get("password_key", "password")
        output_format = self.sys_conf.get("format", "bzip2")
        lower_email_only = self.sys_conf.get("lower_email", "yes") == "yes"
        salt_length = self.sys_conf.get("salt_length", 16)
        by_id_col = self.sys_conf.get("by_id", "uid")

        start_time = datetime.datetime.now()
        with self.open_target_file(filename, output_format) as fp:
            try:
                while offset < rows_num:
                    result = self.select_table_range(table_name,
                                                     offset, each_count,
                                                     by_id_col)
                    for row in result:
                        try:
                            email = row[column_map[email_key]]
                            phone = row[column_map[phone_key]]
                            username = row[column_map[username_key]]
                            password = row[column_map[password_key]]

                            if lower_email_only and email:
                                email = email.lower()

                            email = checker.check_email(email)
                            phone = checker.check_phone(phone)

                            fields = {
                                "email": _email_map_hook(email),
                                "phone": _phone_map_hook(phone),
                                "username": _username_map_hook(username),
                            }

                            password = _password_map_hook(password)

                            logging.debug("%s  %s %s %s", list(row),
                                          email, phone, password)

                            content = hascrpt.hash_info(hash_method,
                                                        salt_length=salt_length,
                                                        password=password,
                                                        **fields)
                            content = _content_final_hook(content)
                            logging.debug("Content: %s", content)
                            fp.write(json.dumps(content) + "\n")
                            dump_count += 1

                        except Exception as ex:
                            logging.error("ERROR FOR DATA: %s", ex)
                            logging.error("ERROR DATA: %s", row)

                    offset += len(result)
                    logging.info("%s of %s/%s records dump",dump_count, offset, rows_num)

            except Exception as ex:
                logging.error("Error: %s", ex)

            except KeyboardInterrupt:
                logging.error("Stop by user")

        finish_time = datetime.datetime.now()
        total_seconds = (finish_time - start_time).total_seconds()
        logging.info("TOTAL TIME: %ss", total_seconds)
        logging.info("BENCHMARK: Write %s records/s", dump_count / total_seconds)
        logging.info("BENCHMARK: Process %s records/s", offset / total_seconds)


