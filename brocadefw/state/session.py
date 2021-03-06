# -*- coding: utf-8 -*-
""" session関連 """


def generate_id():
	""" セッションIDを生成
	
	@return: セッションID
	"""
	from os import urandom
	from hashlib import md5 as hash
	return hash(urandom(64)).hexdigest()


class Storage(object):
	""" セッションストレージ（保存先に応じて継承すること） """

	def load(self, session_id):
		""" セッションデータをロード
	
		@param session_id: セッションID
		@return: セッションデータ（辞書）
		"""
		raise NotImplementedError("Storage::load")


	def save(self, session_id, data, lifetime):
		""" セッションデータを保存
	
		@param session_id: セッションID
		@param data: セッションデータ（辞書）
		@param lifetime: 有効期間[sec]
		"""
		raise NotImplementedError("Storage::save")



class DictStorage(Storage):
	""" 辞書を使用したセッションストレージ
	以下の理由のため、テスト目的でのみ使用すること
	* セッションの保持期間を指定できないので、古いデータをいつまでも保持してしまう
	* メモリ解放機構を持たないので、大量アクセスでメモリ不足に陥る可能性がある
	* プロセスごとにメモリ空間が独立しているので、マルチプロセス環境で前回アクセス時の状態が復元されない可能性がある（プロセス数分だけ状態が保存され、どれが復元されるかわからない）
	* プロセスが終了すると内容がクリアされる
	"""

	# スレッドセーフにするためのロック機構
	from threading import Lock
	__lock = Lock()

	# キャッシュは全インスタンスで共有
	__cache = {}

	def load(self, session_id):
		with self.__lock:
			return self.__cache.get(session_id, {})


	def save(self, session_id, data, lifetime):
		with self.__lock:
			self.__cache[session_id] = data



class MemcachedStorage(Storage):
	""" memcachedを使用したセッションストレージ（本番環境で使うならこっち） """
	def __init__(self, memcached = None, prefix = "session:"):
		""" コンストラクタ
	
		@param memcached: memcachedオブジェクトまたはサーバ情報のリスト（省略時は "localhost:11211" を開く）
		@param prefix: キーのプレフィックス（プレフィックス＋セッションIDをキーとする）
		"""
		if not self.__is_memcached_instance(memcached):
			# memcachedインスタンスでなければサーバ情報とみなし、新しいインスタンスを生成
			memcached = self.__memcached(memcached)

		self.__cache = memcached
		self.__prefix = prefix
	
	
	def load(self, session_id):
		key = self.__prefix + session_id
		data = self.__cache.get(key)
		if data == None:
			# データがなければ空の辞書を返す
			data = {}

		return data


	def save(self, session_id, data, lifetime):
		key = self.__prefix + session_id
		self.__cache.set(key, data, time = lifetime)


	@staticmethod
	def __is_memcached_instance(obj):
		""" memcachedのインスタンスか？
	
		@param obj: オブジェクト
		@return: memcachedのインスタンスならTrue、そうでなければFalse
		"""
		if hasattr(obj, "get") and hasattr(obj, "set"):
			# get/setメソッドがあればインスタンス
			return True

		return False

	
	@staticmethod
	def __memcached(servers):
		""" memcachedオブジェクトを生成

		@requires: https://pypi.python.org/pypi/python3-memcached/
		@requires: https://pypi.python.org/pypi/python-memcached/
		"""
		if servers == None:
			servers = ["localhost:11211"]

		import memcache
		return memcache.Client(servers)
