#!/usr/bin/python


import logging
import MySQLdb


class Locomotive(object):
    def __init__(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
        self.mysql.autocommit(True)
        self.cursor = self.mysql.cursor()

    def connect_db(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
        self.mysql.autocommit(True)
        self.cursor = self.mysql.cursor()

    def get_table_rows(self, table_name):
        try:
            sql = "SELECT COUNT(*) FROM `%s`" % table_name
            self.cursor.execute(sql)
            return self.cursor.fetchall()[0][0]

        except MySQLdb.ProgrammingError as ex:
            logging.debug("Programming Error: %s", ex)
            return None

    def select_table_range(self, table_name, offset, count):
        sql = "SELECT * FROM `%s` LIMIT %s, %s" % (table_name, offset, count)

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def dump_table(self, table_name, count):
        rows_num = self.get_table_rows(table_name)
        offset = 0

        if rows_num is None:
            logging.error("Table '%s' not found", table_name)
            return

        while offset < rows_num:
            result = self.select_table_range(table_name, offset, count)
            for x in result:
                logging.info("%s", x)

            offset += len(result)

