# -*- coding: utf-8 -*-
""" アプリケーション（WSGI版） """

from brocade import application

class WSGI_Application(application.BaseApplication):
	""" アプリケーション """

	def __call__(self, environ, start_response):
		""" リクエスト処理 """
#		environ["HTTP_ACCEPT_CHARSET"] = "iso-8859-5, unicode-1-1;q=0.8"
#		environ["HTTP_ACCEPT_CHARSET"] = "Shift_JIS,utf-8;q=0.7,*;q=0.7"

		uri = environ.get("PATH_INFO", "")

		(handler, args) = self._get_matched_data(uri)
		handler_instance = handler(environ, start_response)
		yield handler_instance(*args)
