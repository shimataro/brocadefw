# -*- coding: utf-8 -*-
""" KVSキャッシュモジュール """

class BaseCache(object):
	""" ベースクラス """

	def get(self, key, default = None):
		""" 値の取得
		
		@param key: キー
		@param default: 取得できない場合のデフォルト値
		@return: 取得した値
		"""
		raise NotImplementedError()
	
	def set(self, key, value):
		""" 値の設定
		
		@param key: キー
		@param value: 値
		@return: キャッシュオブジェクト
		"""
		raise NotImplementedError()
	
	def delete(self, key):
		""" キーの削除
		
		@param key: キー
		@return: キャッシュオブジェクト
		"""
		raise NotImplementedError()


class DictCache(BaseCache):
	""" 辞書によるインメモリキャッシュ
	
	辞書オブジェクトに保存するのでオブジェクトが破棄されると内容も消えるが、インメモリでプロセス間通信等も行わないので極めて高速
	"""

	def __init__(self):
		self.__cache = {}

	def get(self, key, default = None):
		return self.__cache.get(key, default)
	
	def set(self, key, value):
		self.__cache[key] = value
		return self
		
	def delete(self, key):
		if key in self.__cache:
			del self.__cache[key]

		return self


class ChainCache(BaseCache):
	""" 複数のキャッシュオブジェクトのチェイン
	
	メモリ/ディスク/ネットワーク等、速度が異なる複数の保存先の中から高速なものを優先的に使いたい場合に有用
	"""

	def __init__(self, *cache_list):
		""" コンストラクタ
		
		@param cache_list: キャッシュオブジェクト一覧（先に指定したものがgetで優先的に使われる）
		"""
		self.__cache_list = cache_list
		
	def get(self, key, default = None):
		""" 値の取得（最初に見つかった値を返し、見つからなかったオブジェクトにはその値を入れる） """
		cache_not_found = []
		for cache in self.__cache_list:
			value = cache.get(key, default)
			if value != default:
				# 見つかったらそれまでのオブジェクトに値を設定
				self.__set(cache_not_found, key, value)
				return value

			cache_not_found.append(cache)
			
		return default
	
	def set(self, key, value):
		""" 全てのキャッシュオブジェクトに値を設定 """
		self.__set(self.__cache_list, key, value)
		return self
			
	def delete(self, key):
		""" 全てのキャッシュオブジェクトから値を削除 """
		self.__delete(self.__cache_list, key)
		return self

	@staticmethod
	def __set(cache_list, key, value):
		""" 指定のキャッシュオブジェクトに値を設定
		
		@param cache_list: キャッシュオブジェクト一覧
		@param key: キー
		@param value: 値
		"""
		for cache in cache_list:
			cache.set(key, value)

	@staticmethod
	def __delete(cache_list, key):
		""" 指定のキャッシュオブジェクトから値を削除
		
		@param cache_list: キャッシュオブジェクト一覧
		@param key: キー
		"""
		for cache in cache_list:
			cache.delete(key)


def test():
	""" テスト """
	# 辞書キャッシュのテスト
	dict_cache1 = DictCache()
	dict_cache1.set("a", 1)
	assert dict_cache1.get("a") == 1
	assert dict_cache1.get("b") == None

	# チェインキャッシュのテスト
	dict_cache0 = DictCache()
	dict_cache0.set("b", 2)
	chain_cache = ChainCache(dict_cache0, dict_cache1)
	assert dict_cache0.get("a") == None
	assert chain_cache.get("a") == 1
	assert dict_cache0.get("a") == 1
	assert chain_cache.get("b") == 2
	assert dict_cache1.get("b") == None

	print("OK")


if __name__ == "__main__":
	test()
	