# -*- coding: utf-8 -*-

def create_application():
	""" アプリケーション作成 """
	from brocade.wsgi import application
	return application.WSGI_Application(
		("private.web.default", "Handler"),
		(r"^/$", "private.web.index", "Handler"),
		(r"^/hell$", "private.web.hell", "Handler"),
	)
