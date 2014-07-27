# -*- coding: utf-8 -*-
""" KVSキャッシュモジュール

get/set/deleteメソッドを実装すること
"""
from threading import Lock

class Cache(object):
	""" キャッシュモジュールのベースクラス """

	def get(self, key, default = None):
		""" 値の取得

		@param key: キー
		@param default: 取得できない場合のデフォルト値
		@return: 取得した値
		"""
		raise NotImplementedError("Cache::get")
	
	def set(self, key, value, lifetime = None):
		""" 値の設定

		@param key: キー
		@param value: 値
		@param lifetime: 有効期間[sec] （キャッシュシステムへの提案情報として渡しているが、値がこの期間中保持されていること及びこの期間を経過したら削除されることは保証されない）
		@return: キャッシュオブジェクト
		"""
		raise NotImplementedError("Cache::set")
	
	def delete(self, key):
		""" キーの削除

		@param key: キー
		@return: キャッシュオブジェクト
		"""
		raise NotImplementedError("Cache::delete")


class DictCache(Cache):
	""" 辞書によるインメモリキャッシュ

	辞書オブジェクトに保存するのでオブジェクトが破棄されると内容も消えるが、インメモリでプロセス間通信等も行わないので極めて高速
	"""

	def __init__(self):
		self.__cache = {}

	def get(self, key, default = None):
		return self.__cache.get(key, default)

	def set(self, key, value, lifetime = None):
		self.__cache[key] = value
		return self

	def delete(self, key):
		if key in self.__cache:
			del self.__cache[key]

		return self


class GlobalDictCache(Cache):
	""" グローバル領域に保存する辞書キャッシュ

	スレッドセーフにするためにロックを使用
	"""
	__g_lock_init = Lock()
	__g_lock  = {}
	__g_cache = {}

	def __init__(self, name = ""):
		""" コンストラクタ

		@param name: キャッシュ名
		"""
		with self.__g_lock_init:
			# この名前でロックとキャッシュ領域が作られていなければ作成
			if not name in self.__g_lock:
				self.__g_lock [name] = Lock()
				self.__g_cache[name] = {}

		self.__lock  = self.__g_lock [name]
		self.__cache = self.__g_cache[name]

	def get(self, key, default = None):
		with self.__lock:
			return self.__cache.get(key, default)

	def set(self, key, value, lifetime = None):
		with self.__lock:
			self.__cache[key] = value

		return self

	def delete(self, key):
		with self.__lock:
			if key in self.__cache:
				del self.__cache[key]

		return self


class ChainCache(Cache):
	""" 複数のキャッシュオブジェクトのチェイン

	メモリ/ディスク/ネットワーク等、速度が異なる複数の保存先の中から高速なものを優先的に使いたい場合に有用
	"""

	def __init__(self, *cache_list):
		""" コンストラクタ

		@param cache_list: キャッシュオブジェクト一覧（先に指定したものがgetで優先的に使われる）
		"""
		self.__cache_list = cache_list

	def get(self, key, default = None, lifetime = None):
		""" 値の取得

		最初に見つかった値を返し、見つからなかったオブジェクトにはその値を入れる
		@param key: キー
		@param default: 取得できない場合のデフォルト値
		@param lifetime: 高優先度のキャッシュオブジェクトに値を設定する際の有効期間[sec]
		@return: 取得した値
		"""
		cache_not_found = []
		for cache in self.__cache_list:
			value = cache.get(key, default)
			if value != default:
				# 見つかったらそれまでのオブジェクトに値を設定
				self.__set(cache_not_found, key, value, lifetime)
				return value

			cache_not_found.append(cache)

		return default

	def set(self, key, value, lifetime = None):
		self.__set(self.__cache_list, key, value, lifetime)
		return self

	def delete(self, key):
		""" キーの削除

		全てのキャッシュオブジェクトから値を削除
		@param key: キー
		@return: キャッシュオブジェクト
		"""
		self.__delete(self.__cache_list, key)
		return self


	@staticmethod
	def __set(cache_list, key, value, lifetime):
		""" 指定のキャッシュオブジェクトに値を設定

		@param cache_list: キャッシュオブジェクト一覧
		@param key: キー
		@param value: 値
		"""
		for cache in cache_list:
			cache.set(key, value, lifetime)

	@staticmethod
	def __delete(cache_list, key):
		""" 指定のキャッシュオブジェクトから値を削除

		@param cache_list: キャッシュオブジェクト一覧
		@param key: キー
		"""
		for cache in cache_list:
			cache.delete(key)


def _test():
	""" テスト """
	########################################
	# 辞書キャッシュのテスト
	dict_cache = DictCache()
	dict_cache.set("a", 1)
	assert dict_cache.get("a") == 1
	assert dict_cache.get("b") == None

	########################################
	# グローバル辞書キャッシュのテスト
	global_dict_cache1 = GlobalDictCache()
	global_dict_cache1.set("b", 2)

	# 名前が同じだと同じ値が取り出される
	global_dict_cache2 = GlobalDictCache()
	assert global_dict_cache2.get("b") == 2

	########################################
	# チェインキャッシュのテスト
	chain_cache = ChainCache(dict_cache, global_dict_cache1)

	# dict_cacheになくてglobal_dict_cache1にあるものを取り出したら、取り出した後でdict_cacheにもコピーされる
	assert dict_cache.get("b") == None
	assert chain_cache.get("b") == 2
	assert dict_cache.get("b") == 2

	# global_dict_cache1になくてdict_cacheにあるものを取り出しても、global_dict_cache1にはコピーされない
	assert global_dict_cache1.get("a") == None
	assert chain_cache.get("a") == 1
	assert global_dict_cache1.get("a") == None

	# チェインキャッシュのキーを削除すると全てのキャッシュから削除される
	chain_cache.delete("b")
	assert dict_cache.get("b") == None
	assert global_dict_cache1.get("b") == None

	print("OK")


if __name__ == "__main__":
	_test()
