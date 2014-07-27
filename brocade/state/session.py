# -*- coding: utf-8 -*-
""" session関連 """


def generate_id():
	""" セッションIDを生成
	
	@return: セッションID
	"""
	from os import urandom
	from hashlib import md5 as hash
	return hash(urandom(64)).hexdigest()


class Saver(object):
	""" セッションセーバ（保存先に応じて継承すること） """

	def load(self, session_id):
		""" セッションデータをロード
	
		@param session_id: セッションID
		@return: セッションデータ
		"""
		raise NotImplementedError("Saver::load")


	def save(self, session_id, data, lifetime):
		""" セッションデータを保存
	
		@param session_id: セッションID
		@param data: セッションデータ
		@param lifetime: 有効期間[sec]
		"""
		raise NotImplementedError("Saver::save")



class DictSaver(Saver):
	""" 辞書を使用したセッションセーバ（メモリを圧迫した際の削除機構を持たないので、本番環境では使わないこと） """

	# スレッドセーフにするためのロック機構
	from threading import Lock
	__lock = Lock()

	# キャッシュは全インスタンスで共有
	__cache = {}

	def __init__(self, prefix = "session:"):
		self.__prefix = prefix
	
	
	def load(self, session_id):
		key = self.__prefix + session_id
		with self.__lock:
			data = self.__cache.get(key, None)

		if data == None:
			# データがなければ空の辞書を返す
			data = {}

		return data


	def save(self, session_id, data, lifetime):
		key = self.__prefix + session_id
		with self.__lock:
			self.__cache[key] = data



class MemcachedSaver(Saver):
	""" memcachedを使用したセッションセーバ（本番環境で使うならこっち）

	@requires: https://pypi.python.org/pypi/python3-memcached/
	@requires: https://pypi.python.org/pypi/python-memcached/
	"""
	def __init__(self, servers = ["127.0.0.1:11211"], prefix = "session:"):
		import memcache
		self.__cache = memcache.Client(servers)
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
