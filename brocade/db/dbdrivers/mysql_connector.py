# -*- coding: utf-8 -*-
""" MySQL用ドライバ

@requires: mysql-connector-python ver 1.0 or later
@see: http://dev.mysql.com/doc/connector-python/en/connector-python-reference.html
@see: http://downloads.mysql.com/docs/connector-python-relnotes-en.a4.pdf
"""
from mysql.connector        import MySQLConnection as BaseConnection
from mysql.connector.cursor import MySQLCursor     as BaseCursor


def connect(*args, **kwargs):
	""" Connecionオブジェクト作成 """
	return Connection(*args, **kwargs)


class Connection(BaseConnection):
	""" コネクタ """

	def cursor(self):
		""" カーソル取得

		@return: カーソルオブジェクト
		"""
		return super(Connection, self).cursor(cursor_class = Cursor)


class Cursor(BaseCursor):
	""" カーソル """

	def execute(self, query, *params):
		""" クエリ実行

		@param query: 実行するクエリ（プレースホルダは"?"で統一）
		@param params: パラメータ(tuple)
		"""
		query = query.replace("?", "%s")
		super(Cursor, self).execute(query, params)


	def _row_to_python(self, rowdata, desc = None):
		""" フェッチ行のタプルを辞書に変換

		@see: http://geert.vanderkelen.org/connectorpython-custom-cursors/
		"""
		row = super(Cursor, self)._row_to_python(rowdata, desc)
		if row == None:
			return None

		return dict(zip(self.column_names, row))
