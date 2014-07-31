# -*- coding: utf-8 -*-

from brocade import application_wsgi as application


def create_application(root_dir):
	""" アプリケーション作成

	@param root_dir: アプリケーションのルートディレクトリ
	"""
	return application.WSGI_Application(
		root_dir,
		("private.web.default", "Handler"),
		(r"^/$", "private.web.index", "Handler"),
		(r"^/hell$", "private.web.hell", "Handler"),
	)


class MyBaseHandler(application.WSGI_Handler):
	def session_storage(self):
		""" セッションストレージ取得（DictStorageはテスト用なので、本番環境ではMemcachedStorage等を使うこと） """
		from brocade.state import session
		return session.DictStorage()
