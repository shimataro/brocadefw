# -*- coding: utf-8 -*-
""" DB操作の共通化
PEP249でもバラつきのある仕様を統一＋α

* クエリのプレースホルダを"?"に統一
* フェッチデータの辞書化
@see: http://www.python.org/dev/peps/pep-0249/
"""


def connect(_driver, *args, **kwargs):
	""" DBに接続

	@param _driver: コネクタドライバ名（"dbdrivers"ディレクトリ以下にあるモジュール）
	@param args: コネクタに渡すパラメータ
	@param kwargs: コネクタに渡すパラメータ
	@return: コネクタ
	@raise ImportError: ドライバが見つからない場合に投げる例外
	"""
	from importlib import import_module
	module = import_module("dbdrivers." + _driver)
	return module.connect(*args, **kwargs)


def _test():
	""" 単体テスト """
	print("db test")

	connection = connect(
		"mysql_connector",
		host     = "localhost",
		db       = "example",
		user     = "user",
		passwd   = "password",
		charset  = "utf8",
	)

	cursor = connection.cursor()
	cursor.execute("SELECT * FROM `t_test` WHERE `id` = ?", 1)
	for row in cursor:
		print(row)

	print("OK")


# test
if __name__ == "__main__":
	_test()
