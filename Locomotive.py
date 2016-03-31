#!/usr/bin/python


import MySQLdb


class Locomotive(object):
    def __init__(self):
        self.mysql = MySQLdb.connect()

    def connect(self, *args, **kwargs):
        self.mysql = MySQLdb.connect(*args, **kwargs)
