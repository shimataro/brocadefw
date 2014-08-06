# -*- coding: utf-8 -*-
""" O/Rマッパー

* ID（プライマリキー）は `id` という名前のオートインクリメント値にすること
"""

import rdbutils

class BaseMapper(object):
	""" マッパーのベースクラス """

	# テーブル名（派生クラスで定義すること）
	TABLENAME = None

	# スレッドローカルデータ
	from threading import local
	__tld = local()


	@staticmethod
	def connection_manager():
		""" rdbutils.ConnectionManagerのインスタンスを返すこと """
		raise NotImplementedError("BaseMapper::connection_manager")


	@classmethod
	def create_instance(cls, info):
		""" インスタンスを作成

		@param info: 生成時のデータ
		"""
		# IDは設定不可
		if "id" in info:
			raise AttributeError("ID is set automatically")

		# DBに追加してあらためてインスタンスを取得
		identifier = cls._db_insert(info)
		return cls.get_instance(identifier)


	@classmethod
	def get_instance(_cls, _identifier, *args, **kwargs):
		""" インスタンスを取得

		@param _identifier: インスタンスID
		@param args: verifyに渡すパラメータ
		@param kwargs: verifyに渡すパラメータ
		@return: インスタンス or None
		"""
		obj = _cls.__get_instance(_identifier)
		if obj == None:
			return None

		# 検証
		if not obj.verify(*args, **kwargs):
			return None

		return obj


	def __init__(self, info):
		self.__info = info.copy()
		self.rollback()


	def __enter__(self):
		self.commit()
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		if exc_type != None:
			self.rollback()
			return False

		self.commit()
		return True


	def verify(self):
		""" オブジェクトの検証
		所有者の確認等、検証処理を行う場合はオーバーライドすること

		@return: OK/NG
		"""
		return True


	def id(self):
		""" ID取得 """
		return self.get("id")


	def get(self, name):
		""" 要素値取得

		@param name: 要素名
		@return: 要素値
		"""
		return self.__info_merged[name]


	def set(self, name, value, commit = False):
		""" 要素設定

		@param name: 要素名
		@param value: 要素値
		@param commit: 設定をすぐに反映させるならTrue
		"""
		# IDは変更不可
		if name == "id":
			raise AttributeError("ID is immutable")

		if not name in self.__info:
			raise KeyError("table `%s` does not have column `%s`" % (self.TABLENAME, name))

		# オリジナルと同じ値を設定した場合
		if value == self.__info[name]:
			# ダーティーバッファを削除
			if name in self.__info_dirty:
				del self.__info_dirty[name]

		else:
			self.__info_dirty[name] = value
			self.__info_merged[name] = value

		if commit:
			self.commit()


	def commit(self):
		""" 変更を確定 """
		if not self.is_dirty():
			return

		self._db_set(self.id(), self.__info_dirty)
		self.__info = self.__info_merged.copy()
		self.__info_dirty = {}


	def rollback(self):
		""" 元の状態（オブジェクト生成時または最後のコミット時）に戻す """
		self.__info_dirty = {}
		self.__info_merged = self.__info.copy()


	def is_dirty(self):
		""" 元の状態から変更されたか？

		@return: Yes/No
		"""
		return len(self.__info_dirty) > 0


	@classmethod
	def _db_get(cls, identifier):
		""" DBからデータ取得
		memcached等のキャッシュを挟む場合はオーバーライドすること

		@param identifier: ID
		@return: 取得データ or None
		"""
		cm = cls.connection_manager()
		with cm as cursor:
			query = "SELECT * FROM `%s` WHERE `id` = ? LIMIT 1" % (cls.TABLENAME)
			cursor.execute(*cm.xquery(query, identifier))

			# データ取得
			row = cursor.fetchone()
			if row == None:
				return None

			return rdbutils.row_tuple2dict(cursor, row)


	@classmethod
	def _db_set(cls, identifier, info):
		""" DBのデータ変更
		memcached等のキャッシュを挟む場合はオーバーライドすること

		@param identifier: ID
		@param info: 格納情報
		@return: 取得データ or None
		"""
		# クエリ生成
		sets, params = rdbutils.query_set(info)
		query = "UPDATE `%s` SET %s WHERE `id` = ?" % (cls.TABLENAME, sets)
		params.append(identifier)

		# クエリ実行
		cm = cls.connection_manager()
		with cm as cursor:
			cursor.execute(*cm.xquery(query, *params))


	@classmethod
	def _db_insert(cls, info):
		""" DBにデータ格納

		@param info: 格納情報
		@return: RowID
		"""
		# クエリ生成
		into, values, params = rdbutils.query_insert(info)
		query = "INSERT INTO `%s`(%s) VALUES(%s)" % (cls.TABLENAME, into, values)

		# クエリ実行
		cm = cls.connection_manager()
		with cm as cursor:
			cursor.execute(*cm.xquery(query, *params))
			return cursor.lastrowid


	@classmethod
	def __get_instance(cls, identifier):
		""" インスタンスを作成（本体）
		インスタンスの検証は呼び出し元のget_instanceで行う

		@param identifier: インスタンスID
		@return: インスタンス or None
		"""
		# キャッシュを調べる
		key = "%s:%d" % (cls.TABLENAME, identifier)
		obj = cls.__cache_get(key)
		if obj != None:
			return obj

		# なければDBから取得
		row = cls._db_get(identifier)
		if row == None:
			return None

		# キャッシュに格納
		obj = cls(row)
		cls.__cache_set(key, obj)
		return obj


	@classmethod
	def __cache_get(cls, key):
		""" キャッシュのオブジェクトを取得

		@param key: キー
		@return: オブジェクト or None
		"""
		try:
			return cls.__tld.cache.get(key)

		except AttributeError:
			from weakref import WeakValueDictionary
			cls.__tld.cache = WeakValueDictionary()
			return None


	@classmethod
	def __cache_set(cls, key, obj):
		""" キャッシュにオブジェクトを設定

		@param key: キー
		@param obj: オブジェクト
		"""
		cls.__tld.cache[key] = obj


def _test():
	""" テスト """

	# SQLiteで試してみる
	cm = rdbutils.ConnectionManager("sqlite3", ":memory:")

	# テスト用マッパー
	class TestMapper(BaseMapper):
		TABLENAME = "t_test"

		@staticmethod
		def connection_manager():
			return cm


	print("mapper")

	# テーブル作成
	with cm as cursor:
		cursor.execute("CREATE TABLE `t_test`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `value` TEXT)")

	obj1 = TestMapper.create_instance({"value": "atai"})
	obj2 = TestMapper.get_instance(1)

	# obj1を変更→obj2にも反映されているはず
	key = "value"
	val = "val"
	obj1.set(key, val, True)
	assert obj1.get(key) == val

	# withの前後で自動的にcommitされる
	with obj2:
		key = "value"
		val = "value"
		obj2.set(key, val)
	assert obj1.get(key) == val

	# IDは変更不可（AttributeError）
	try:
		obj1.set("id", 0)
		assert False
	except AttributeError:
		assert True

	# 存在しないキーを変更ししたらKeyError
	try:
		obj2.set("nonekey", 0)
		assert False
	except KeyError:
		assert True

	print("OK")


if __name__ == "__main__":
	_test()
