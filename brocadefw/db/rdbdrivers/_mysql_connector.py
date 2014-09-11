# -*- coding: utf-8 -*-

import mysql.connector as connector

from . import trans_query, BaseConnectionManager, BaseCursor

class ConnectionManager(BaseConnectionManager):
	def __init__(self, *args, **kwargs):
		return super(ConnectionManager, self).__init__(connector, *args, **kwargs)


	def _cursor(self, *args, **kwargs):
		""" カーソル取得

		@return: カーソルオブジェクト
		"""
		return super(ConnectionManager, self)._cursor(cursor_class = _Cursor)


class _Cursor(connector.cursor.MySQLCursor, BaseCursor):
	def execute(self, query, *params):
		tr = trans_query(connector.paramstyle, query, params)
		return super(_Cursor, self).execute(*tr)


	def _row_to_python(self, rowdata, desc=None):
		# http://geert.vanderkelen.org/connectorpython-custom-cursors/
		row = super(_Cursor, self)._row_to_python(rowdata, desc)
		if row:
			return dict(zip(self.column_names, row))

		return None
