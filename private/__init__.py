# -*- coding: utf-8 -*-

def create_application():
	""" アプリケーション作成 """
	from brocade import wsgi
	return wsgi.WSGI_Application(
		("private.web.default", "Handler"),
		(r"^/$", "private.web.index", "Handler"),
		(r"^/hell$", "private.web.hell", "Handler"),
	)
