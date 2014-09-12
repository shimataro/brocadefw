# -*- coding: utf-8 -*-
""" O/Rマッパー

* ID（プライマリキー）は `id` という名前のオートインクリメント値にすること
"""

if __name__ == "__main__":
	import rdbutils
else:
	from . import rdbutils

class BaseMapper(object):
	""" マッパーのベースクラス """

	# テーブル名（派生クラスで定義すること）
	TABLENAME = None

	# IDのカラム名
	ID_NAME = "id"

	# スレッドローカルデータ
	from threading import local
	__tld = local()


	@classmethod
	def connection_manager(cls):
		""" rdbutils.ConnectionManagerのインスタンスを返すこと """
		raise NotImplementedError("BaseMapper::connection_manager")


	@classmethod
	def get_instance(cls, _identifier, *args, **kwargs):
		""" インスタンスを取得

		@param _identifier: インスタンスID
		@param args: verifyに渡すパラメータ
		@param kwargs: verifyに渡すパラメータ
		@return: インスタンス or None
		"""
		obj = cls.__get_instance(_identifier)
		if obj == None:
			return None

		# 検証
		if not obj.verify(*args, **kwargs):
			return None

		return obj


	@classmethod
	def get_instance_by_unique(cls, _unique, *args, **kwargs):
		""" ユニーク情報からインスタンスを取得

		@param _identifier: インスタンスID
		@param args: verifyに渡すパラメータ
		@param kwargs: verifyに渡すパラメータ
		@return: インスタンス or None
		"""
		identifier = cls._u2id(_unique)
		return cls.get_instance(identifier, *args, **kwargs)


	@classmethod
	def add_instance(cls, _info, *args, **kwargs):
		""" インスタンスを作成

		@param _info: 生成時のデータ
		@param args: verifyに渡すパラメータ
		@param kwargs: verifyに渡すパラメータ
		"""
		# IDは設定不可
		if cls.ID_NAME in _info:
			raise AttributeError("ID is generated automatically")

		# DBに追加してあらためてインスタンスを取得
		identifier = cls._db_add(_info)
		return cls.get_instance(identifier, *args, **kwargs)


	def __init__(self, info):
		""" コンストラクタ

		@param info: オブジェクト情報
		"""
		self.__info = info.copy()
		self.rollback()


	def __del__(self):
		""" デストラクタ """
		self.commit()


	def __enter__(self):
		""" コンテキストマネージャ
		開始時にコミットする
		"""
		self.commit()
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		""" コンテキストマネージャ
		終了時にコミットする
		"""
		if exc_type != None:
			self.rollback()
			return False

		self.commit()
		return True


	def verify(self):
		""" オブジェクトの検証
		所有者の確認や削除フラグの確認等、オブジェクトの検証を行う場合はオーバーライドすること

		@return: OK/NG
		"""
		return True


	def get(self, name):
		""" 要素値取得

		@param name: 要素名
		@return: 要素値
		"""
		return self.__info_merged[name]


	def get_multi(self, columns = None):
		""" 複数要素取得

		@param columns: 取得するカラム（省略時は全要素）
		@return: 要素
		"""
		if columns == None:
			return self.__info_merged.copy()

		result = {}
		for column in columns:
			if column in self.__info_merged:
				result[column] = self.__info_merged[column]

		return result


	def set(self, name, value, commit = False):
		""" 要素設定

		@param name: 要素名
		@param value: 要素値
		@param commit: 設定をすぐに反映させるならTrue
		"""
		# IDは変更不可
		if name == self.ID_NAME:
			raise AttributeError("ID is immutable")

		if not name in self.__info:
			raise KeyError("table `{tablename}` does not have column `{columnname}`".format(tablename = self.TABLENAME, columnname = name))

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


	def set_multi(self, info, columns = None, commit = False):
		""" 要素一括設定

		@param info: 設定情報
		@param columns: この中にキーがあるものだけ対象とする
		@param commit: 設定をすぐに反映させるならTrue
		"""
		if columns == None:
			for column, value in info.items():
				self.set(column, value)

		else:
			for column in columns:
				if column in info:
					value = info[column]
					self.set(column, value)

		if commit:
			self.commit()


	def delete(self):
		""" インスタンスを削除
		これ以降のインスタンスへのアクセス結果は保証されない

		@param obj: 削除するオブジェクト
		"""
		identifier = self.identifier
		self._db_del(identifier)

		key = self.__cache_key(identifier)
		self.__cache_del(key)


	def commit(self):
		""" 変更を確定 """
		if not self.is_dirty:
			return

		self._db_set(self.identifier, self.__info_dirty, self.__info_merged)
		self.__info = self.__info_merged.copy()
		self.__info_dirty = {}


	def rollback(self):
		""" 元の状態（オブジェクト生成時または最後のコミット時）に戻す """
		self.__info_dirty = {}
		self.__info_merged = self.__info.copy()


	@property
	def identifier(self):
		""" ID取得 """
		return self.get(self.ID_NAME)


	@property
	def is_dirty(self):
		""" 元の状態から変更されたか？

		@return: Yes/No
		"""
		return len(self.__info_dirty) > 0


	@classmethod
	def _u2id(cls, unique):
		""" ユニーク情報からIDを取得
		@param unique: ユニーク情報; 辞書
		@return: ID or None
		"""
		with cls.connection_manager() as cursor:
			# データ取得
			row = cursor.select(cls.TABLENAME, unique, cls.ID_NAME)
			if row == None:
				return None

			return row[cls.ID_NAME]


	@classmethod
	def _db_get(cls, identifier):
		""" DBからデータ取得
		memcached等のキャッシュを挟む場合はオーバーライドすること

		@param identifier: ID
		@return: 取得データ or None
		"""
		with cls.connection_manager() as cursor:
			# データ取得
			row = cursor.select(cls.TABLENAME, {cls.ID_NAME: identifier})
			if row == None:
				return None

			return row


	@classmethod
	def _db_set(cls, identifier, info, info_all):
		""" DBのデータ変更
		memcached等のキャッシュを挟む場合はオーバーライドすること

		@param identifier: ID
		@param info: 格納情報; 変更部分のみ
		@param info_all: 格納情報; 全て
		@return: 取得データ or None
		"""
		with cls.connection_manager() as cursor:
			cursor.update(cls.TABLENAME, {cls.ID_NAME: identifier}, info)


	@classmethod
	def _db_add(cls, info):
		""" DBにデータ格納

		@param info: 格納情報
		@return: RowID
		"""
		# クエリ実行
		with cls.connection_manager() as cursor:
			return cursor.insert(cls.TABLENAME, info)


	@classmethod
	def _db_del(cls, identifier):
		""" DBからデータ削除
		memcached等のキャッシュも消す、DBから消さずに削除フラグを立てるといった場合はオーバーライドすること

		@param identifier: 削除するID
		"""
		with cls.connection_manager() as cursor:
			cursor.delete(cls.TABLENAME, {cls.ID_NAME: identifier})


	@classmethod
	def __get_instance(cls, identifier):
		""" インスタンスを作成（本体）
		インスタンスの検証は呼び出し元のget_instanceで行う

		@param identifier: インスタンスID
		@return: インスタンス or None
		"""
		# キャッシュを調べる
		key = cls.__cache_key(identifier)
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
	def __cache_key(cls, identifier):
		""" キャッシュのキーを生成

		@param identifier: オブジェクトID
		@return: キー
		"""
		return "{tablename}:{id}".format(tablename = cls.TABLENAME, id = identifier)


	@classmethod
	def __cache_get(cls, key):
		""" キャッシュのオブジェクトを取得

		@param key: キー
		@return: オブジェクト or None
		"""
		try:
			return cls.__tld.cache[key]

		except KeyError:
			return None

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


	@classmethod
	def __cache_del(cls, key):
		""" キャッシュからオブジェクトを削除

		@param key: キー
		"""
		del cls.__tld.cache[key]


def _test():
	""" テスト """
	print("mapper")

	cm = rdbutils.connect("sqlite3", ":memory:")
	with cm as cursor:
		cursor.execute("CREATE TABLE `t_test`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `value1` TEXT, `value2` TEXT)")

	# テスト用マッパー
	class TestMapper(BaseMapper):
		TABLENAME = "t_test"

		@classmethod
		def connection_manager(cls):
			return cm


	obj1 = TestMapper.add_instance({"value1": "atai1", "value2": "atai2"})
	obj2 = TestMapper.get_instance(1)

	# obj1を変更→obj2にも反映されているはず
	obj1.set("value1", "val1", True)
	assert obj1.get("value1") == "val1"

	# withの前後で自動的にcommitされる
	with obj2:
		obj2.set_multi({"value1": "a1", "value2": "a2"})
	assert obj1.get("value1") == "a1"
	assert obj1.get("value2") == "a2"

	# IDは変更不可（AttributeError）
	try:
		obj1.set("id", 0)
		assert False
	except AttributeError:
		assert True

	# 存在しないキーを変更ししたらKeyError
	try:
		obj2.set("dummykey", 0)
		assert False
	except KeyError:
		assert True

	# 削除したらキャッシュからも消える＝新しいインスタンスは取得できない
	obj1.delete()
	obj3 = TestMapper.get_instance(1)
	assert obj3 == None

	print("OK")


if __name__ == "__main__":
	_test()
