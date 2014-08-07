# -*- coding: utf-8 -*-
""" RDBユーティリティ """


def query_set(data, columns = None):
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


def query_insert(data, columns = None):
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


def row_tuple2dict(cursor, row):
	""" タプル型の行データを辞書型に変換

	@param cursor: カーソルオブジェクト
	@param row: 行データ(tuple)
	@return: 行データ(dict)
	@see: http://docs.python.jp/3.3/library/sqlite3.html
	"""
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]

	return d


class ConnectionManager(object):
	""" 接続マネージャ

	* クエリのプレースホルダを"?"に統一
	* コンテキストマネージャによる自動コミットサポート
	with connection_wrapper as cursor: ...
	"""

	def __init__(self, _connector, *args, **kwargs):
		""" コンストラクタ

		@param _connector: コネクタモジュール（モジュールまたはモジュール名）
		"""
		if type(_connector) == str:
			# 文字列ならロード
			from importlib import import_module
			self.__connector = import_module(_connector)
	
		else:
			# そうでなければモジュール
			self.__connector = _connector
		
		self.__connection = self._connect(*args, **kwargs)
		self.__cursor = None


	def __enter__(self):
		self.__cursor = self._cursor()
		return self.__cursor


	def __exit__(self, exc_type, exc_value, traceback):
		self.__cursor.close()
		self.__cursor = None

		connection = self.connection()
		if exc_type != None:
			# 例外が発生したらロールバック
			connection.rollback()
			return False

		# 正常終了したらコミット
		connection.commit()
		return True


	def connection(self):
		""" 接続オブジェクトを取得

		@return: 接続オブジェクト
		"""
		return self.__connection


	def xquery(self, _query, *args):
		""" パラメータつきクエリを適切なフォーマットに変換

		@param _query: パラメータつきクエリ（プレースホルダは"?"）
		@param args: パラメータ
		@return: 変換後のクエリ, パラメータ
		"""
		paramstyle = self.__connector.paramstyle
		params = args
		if paramstyle == "qmark":
			# 疑問符に対応していればそのまま返す
			query = _query
			return (query, params)

		if paramstyle == "format":
			# printfスタイルに対応していれば"%s"に置き換え
			query = _query.replace("?", "%s")
			return (query, params)

		query = ""
		if paramstyle != "numeric":
			params = {}

		# クエリを"?"で分割
		pieces = _query.split("?")
		length = len(pieces)
		for i, p in enumerate(pieces):
			query += p
			number = i + 1
			if number == length:
				# 最後
				break

			if paramstyle == "numeric":
				# :1, :2, :3, ...
				name = "%d" % number
				query += ":%s" % name

			if paramstyle == "named":
				# :p1, :p2, :p3, ...
				name = "p%d" % number
				query += ":%s" % name
				params[name] = args[i]

			if paramstyle == "pyformat":
				# %(p1)s, %(p2)s, %(p3)s, ...
				name = "p%d" % number
				query += "%%(%s)s" % name
				params[name] = args[i]

		return (query, params)


	def _connect(self, *args, **kwargs):
		""" DBに接続
	
		@return: 接続オブジェクト
		"""
		return self.__connector.connect(*args, **kwargs)
	
	
	def _cursor(self, *args, **kwargs):
		""" カーソル取得
		
		@return: カーソルオブジェクト
		"""
		return self.connection().cursor(*args, **kwargs)


def _test():
	""" テスト """
	print("dbwrapper")

	cm = ConnectionManager("sqlite3", ":memory:")

	# テーブル作成
	with cm as cursor:
		cursor.execute("CREATE TABLE `t_test`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `value` TEXT)")

	# データ作成
	with cm as cursor:
		cursor.execute(*cm.xquery("INSERT INTO `t_test`(`value`) VALUES(?)", "name"))
		cursor.execute(*cm.xquery("INSERT INTO `t_test`(`value`) VALUES(?)", "namae"))
		cursor.execute(*cm.xquery("INSERT INTO `t_test`(`value`) VALUES(?)", "nomen"))

		# 注入してみる
		cursor.execute(*cm.xquery("INSERT INTO `t_test`(`value`) VALUES(?)", "1);DELETE FROM `t_test`;--"))

	# データの確認
	with cm as cursor:
		cursor.execute("SELECT * FROM `t_test` ORDER BY `id`")
		for row in cursor:
			print(row_tuple2dict(cursor, row))

	print("OK")


if __name__ == "__main__":
	_test()
