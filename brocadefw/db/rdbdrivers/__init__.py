# -*- coding: utf-8 -*-
from .. import rdbutils

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
		self.__cursors = []


	def __enter__(self):
		# カーソルを取得
		cursor = self._cursor()
		self.__cursors.append(cursor)
		return cursor


	def __exit__(self, exc_type, exc_value, traceback):
		# カーソルを破棄
		cursor = self.__cursors.pop()
		cursor.close()

		if len(self.__cursors) > 0:
			return False

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


class BaseCursor(object):
	""" カーソル

	* "select", "update", "insert", "delete"を実装
	"""
	def count(self, tablename, condition):
		""" 条件に合うレコード数を取得

		@param tablename: テーブル名
		@param condition: 条件
		@return: レコード数
		"""
		where, params = rdbutils.clause_where(condition)
		query = "SELECT COUNT(*) AS `count` FROM `{tablename}` WHERE {where} LIMIT 1".format(tablename = tablename, where = where)
		self.execute(query, *params)
		row = self.fetchone()
		if row == None:
			return 0

		return row["count"]


	def select(self, tablename, unique, *columns):
		""" テーブルからデータを1件取得

		@param tablename: テーブル名
		@param unique: 一意条件; 辞書
		@param columns: 取得カラム; 省略時は全て
		@return: レコード
		"""
		c = None
		if len(columns) == 0:
			c = "*"
		else:
			c = ",".join("`{column}`".format(column = column) for column in columns)

		where, params = rdbutils.clause_where(unique)
		query = "SELECT {columns} FROM `{tablename}` WHERE {where} LIMIT 1".format(columns = c, tablename = tablename, where = where)
		self.execute(query, *params)
		return self.fetchone()


	def update(self, tablename, unique, data, columns = None):
		""" テーブルのレコードを1件更新

		@param tablename: テーブル名
		@param unique: 一意条件; 辞書
		@param data: 更新データ; 辞書
		@param columns: dataの中で特定のカラムだけ使用する場合はカラムのリストを指定
		"""
		sets, params_set = rdbutils.clause_set(data, columns)
		where, params_where = rdbutils.clause_where(unique)
		query = "UPDATE `{tablename}` SET {sets} WHERE {where} LIMIT 1".format(tablename = tablename, sets = sets, where = where)
		self.execute(query, *(params_set + params_where))


	def insert(self, tablename, data, columns = None):
		""" テーブルに1件レコード挿入

		@param tablename: テーブル名
		@param data: 挿入するデータ; 辞書
		@param columns: dataの中で特定のカラムだけ使用する場合はカラムのリストを指定
		@return: RowID
		"""
		into, values, params = rdbutils.clause_insert(data, columns)
		query = "INSERT INTO `{tablename}`({into}) VALUES({values})".format(tablename = tablename, into = into, values = values)
		self.execute(query, *params)
		return self.lastrowid


	def delete(self, tablename, unique):
		""" テーブルからレコードを1件削除

		@param tablename: テーブル名
		@param unique: 条件; 辞書
		"""
		where, params = rdbutils.clause_where(unique)
		query = "DELETE FROM `{tablename}` WHERE {where} LIMIT 1".format(tablename = tablename, where = where)
		self.execute(query, *params)
