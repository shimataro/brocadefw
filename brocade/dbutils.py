# -*- coding: utf-8 -*-
""" DB操作の共通化

@see: http://www.python.org/dev/peps/pep-0249/
@see: http://dev.mysql.com/doc/connector-python/en/connector-python-reference.html
@see: http://docs.python.jp/3.3/library/sqlite3.html
@see: http://downloads.mysql.com/docs/connector-python-relnotes-en.a4.pdf
@see: http://geert.vanderkelen.org/fetching-rows-as-dictionaries-with-mysql-connectorpython/
@author: shimataro
"""

import mysql.connector


class Connection(mysql.connector.MySQLConnection):
	""" DB接続クラス

	カーソル取得時のパラメータ等、接続に関する操作を統一
	"""

	def cursor(self, bytes_to_str = True, row_to_dict = True):
		""" カーソル取得

		@param bytes_to_str: bytes型を文字列型に変換するか？
		@param row_to_dict: 行を辞書型に変換するか？
		@return: カーソルオブジェクト
		"""
		self.__bytes_to_str = bytes_to_str
		self.__row_to_dict  = row_to_dict
		return self.__super().cursor(prepared = True, cursor_class = Cursor)


	def get_rows(self, count = None, binary = False, columns = None):
		""" 行を取得（必要ならbytes→文字列型の変換＆タプル型→辞書型への変換） """
		(rows, eof) = self.__super().get_rows(count, binary, columns)

		rows_ = []
		charset = self.python_charset
		for row in rows:
			if self.__bytes_to_str:
				row = self.__bytes2str(row, charset)

			if self.__row_to_dict:
				row = self.__row2dict(row, columns)

			rows_.append(row)

		return (rows_, eof)


	@staticmethod
	def __bytes2str(row, charset):
		""" 行データ内のbytes型をstr型に変換

		@param row: 行データ
		@return: str型に変換した後のデータ
		"""
		res = []
		for col in row:
			if type(col) is bytes:
				col = col.decode(charset)

			res.append(col)

		return tuple(res)


	@staticmethod
	def __row2dict(row, columns):
		""" 行データを辞書型に変換

		@param row: 行データ(tuple)
		"""
		res = {}
		for i, v in enumerate(row):
			k = columns[i][0]
			res[k] = v

		return res


	def __super(self):
		return super(Connection, self)


class Cursor(mysql.connector.cursor.MySQLCursorPrepared):
	""" カーソルクラス

	クエリのプレースホルダを統一
	フェッチデータの辞書化
	ユーザが直接作成することはない
	"""

	def execute(self, query, *params):
		""" クエリ実行

		@param query: 実行するクエリ（プレースホルダは"?"で統一）
		@param params: パラメータ(tuple)
		"""
#		query = query.replace("?", "%s")
		self.__super().execute(query, params)


	def __super(self):
		return super(Cursor, self)


def test():
	""" 単体テスト """
	print("db test")

	connector = Connection(
		host     = "localhost",
		db       = "example",
		user     = "user",
		passwd   = "password",
		charset  = "utf8",
	)

	cursor = connector.cursor()
	cursor.execute("SELECT * FROM `t_test` WHERE `id` = ?", 1)
	for row in cursor:
		print(row)

	print("OK")


# test
if __name__ == "__main__":
	test()
