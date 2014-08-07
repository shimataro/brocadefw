# -*- coding: utf-8 -*-

def row2dict(cursor, row):
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


def trans_query(paramstyle, query, params):
	""" パラメータつきクエリを適切なフォーマットに変換

	@param paramstyle: パラメータの形式
	@param query: パラメータつきクエリ（プレースホルダは"?"）
	@param params: パラメータシーケンス
	@return: 変換後のクエリ, パラメータ
	@raise ValueError: 不明なparamstyle
	"""
	if paramstyle == "qmark":
		return _trans_query_qmark   (query, params)

	if paramstyle == "format":
		return _trans_query_format  (query, params)

	if paramstyle == "numeric":
		return _trans_query_numeric (query, params)

	if paramstyle == "named":
		return _trans_query_named   (query, params)

	if paramstyle == "pyformat":
		return _trans_query_pyformat(query, params)

	raise ValueError("unrecognized paramstyle: %s" % paramstyle)


def _trans_query_qmark(query, params):
	# 疑問符に対応していればそのまま返す
	return query, params


def _trans_query_format(query, params):
	# printfスタイルに対応していれば"%s"に置き換え
	query_ = query.replace("?", "%s")
	return (query_, params)


def _trans_query_numeric(query, params):
	# クエリを"?"で分割
	pieces = query.split("?")
	query_ = pieces[0]
	i = 1
	for param in params:
		# :1, :2, :3, ...
		name = "%d" % i
		query_ += ":%s" % name
		query_ += pieces[i]
		i += 1

	return (query_, params)


def _trans_query_named(query, params):
	# クエリを"?"で分割
	pieces = query.split("?")
	query_  = pieces[0]
	params_ = {}
	i = 1
	for param in params:
		# :p1, :p2, :p3, ...
		name = "p%d" % i
		query_ += ":%s" % name
		query_ += pieces[i]
		params_[name] = param
		i += 1

	return (query_, params_)


def _trans_query_pyformat(query, params):
	# クエリを"?"で分割
	pieces = query.split("?")
	query_  = pieces[0]
	params_ = {}
	i = 1
	for param in params:
		# %(p1)s, %(p2)s, %(p3)s, ...
		name = "p%d" % i
		query_ += "%%(%s)s" % name
		query_ += pieces[i]
		params_[name] = param

		i += 1

	return (query_, params_)


class BaseConnectionManager(object):
	""" 接続マネージャ

	* クエリのプレースホルダを"?"に統一
	* コンテキストマネージャによる自動コミットサポート
	with connection_wrapper as cursor: ...
	"""

	def __init__(self, _connector, *args, **kwargs):
		""" コンストラクタ

		@param _connector: コネクタモジュール
		"""
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
