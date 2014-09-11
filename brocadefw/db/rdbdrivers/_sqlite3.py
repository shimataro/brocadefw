# -*- coding: utf-8 -*-

import sqlite3 as connector

from . import row2dict, trans_query, BaseConnectionManager, BaseCursor

class ConnectionManager(BaseConnectionManager):
	def __init__(self, *args, **kwargs):
		return super(ConnectionManager, self).__init__(connector, *args, **kwargs)


	def _connect(self, *args, **kwargs):
		connection = super(ConnectionManager, self)._connect(*args, **kwargs)
		connection.row_factory = row2dict
		return connection


	def _cursor(self, *args, **kwargs):
		return super(ConnectionManager, self)._cursor(_Cursor)


class _Cursor(connector.Cursor, BaseCursor):
	def execute(self, query, *params):
		tr = trans_query(connector.paramstyle, query, params)
		return super(_Cursor, self).execute(*tr)
