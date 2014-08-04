# -*- coding: utf-8 -*-
""" SQLite3用ドライバ

@see: http://docs.python.jp/3.3/library/sqlite3.html
"""


def connect(*args, **kwargs):
	""" Connecionオブジェクト作成 """
	import sqlite3
	connection = sqlite3.connect(*args, **kwargs)
	connection.row_factory = sqlite3.Row
	return connection
