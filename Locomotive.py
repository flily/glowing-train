#!/usr/bin/python


import MySQLdb


class Locomotive(object):
    def __init__(self):
        self.mysql = MySQLdb.connect()
        self.mysql.autocommit(True)
        self.cursor = self.mysql.cursor()

    def connect(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
        self.cursor = self.mysql.cursor()

    def get_table_rows(self, table_name):
        sql = "SELECT COUNT(*) FROM %s" % table_name
        self.cursor.execute(sql)
        return self.cursor.fetchall()[0]
