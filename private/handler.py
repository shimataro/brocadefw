# -*- coding: utf-8 -*-

from brocade import wsgi

class MyBaseHandler(wsgi.WSGI_Handler):
	def session_saver(self):
		""" セッションセーバを取得（DictSaverはテスト用なので、本番環境ではMemcachedSaver等を使うこと） """
		from brocade.state import session
		return session.DictSaver()
