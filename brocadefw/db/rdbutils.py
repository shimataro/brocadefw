# -*- coding: utf-8 -*-
""" RDBユーティリティ

* クエリパラメータを"?"で統一
* コンテキストマネージャ対応（with connection_manager as cursor）
* SET句、INSERT句の生成関数
"""


def connect(_driver, *args, **kwargs):
	""" コネクションマネージャを作成

	@param _driver: ドライバ名
	@param *args: コネクションマネージャに渡す引数
	@param **kwargs: コネクションマネージャに渡す引数
	"""
	from importlib import import_module
	module = import_module("brocadefw.db.rdbdrivers._" + _driver)
	return module.ConnectionManager(*args, **kwargs)


def clause_set(data, columns = None):
	""" SET句とパラメータを生成

	@param data: 設定するデータ
	@param columns: dataの中で、この中にキーがあるものだけ対象とする
	@return: (SET句, パラメータリスト）
	"""
	sets   = []
	params = []
	if columns == None:
		for name, value in data.items():
			sets.append("`%s` = ?" % name)
			params.append(value)

	else:
		for column in columns:
			if column in data:
				sets.append("`%s` = ?" % column)
				params.append(data[column])

	return ",".join(sets), params


def clause_insert(data, columns = None):
	""" INSERT句とパラメータを生成

	@param data: 設定するデータ
	@param columns: dataの中で、この中にキーがあるものだけ対象とする
	@return: (INTO, VALUES, パラメータリスト）
	"""
	into   = []
	values = []
	params = []
	if columns == None:
		for name, value in data.items():
			into  .append("`%s`" % name)
			values.append("?")
			params.append(value)

	else:
		for column in columns:
			if column in data:
				into  .append("`%s`" % column)
				values.append("?")
				params.append(data[column])

	return ",".join(into), ",".join(values), params



def _test():
	""" テスト """
	print("dbwrapper")

	cm = connect("sqlite3", ":memory:")

	# テーブル作成
	with cm as cursor:
		cursor.execute("CREATE TABLE `t_test`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `value` TEXT)")

	# データ作成
	with cm as cursor:
		cursor.execute("INSERT INTO `t_test`(`value`) VALUES(?)", "name")
		cursor.execute("INSERT INTO `t_test`(`value`) VALUES(?)", "namae")
		cursor.execute("INSERT INTO `t_test`(`value`) VALUES(?)", "nomen")

		# 注入してみる
		cursor.execute("INSERT INTO `t_test`(`value`) VALUES(?)", "1);DELETE FROM `t_test`;--")

	# データの確認
	with cm as cursor:
		cursor.execute("SELECT * FROM `t_test` ORDER BY `id`")
		for row in cursor:
			print(row)

	print("OK")


if __name__ == "__main__":
	_test()
