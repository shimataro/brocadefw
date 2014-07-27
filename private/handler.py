# -*- coding: utf-8 -*-

from brocade import wsgi

class MyBaseHandler(wsgi.WSGI_Handler):
	def session_storage(self):
		""" セッションストレージ取得（DictStorageはテスト用なので、本番環境ではMemcachedStorage等を使うこと） """
		from brocade.state import session
		return session.DictStorage()
