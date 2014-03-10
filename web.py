#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

def main():
	from wsgiref.simple_server import make_server
	from brocade.wsgi import application

	application = application.WSGI_Application(
		("private.web.default", "Handler"),
		(r"^/$", "private.web.index", "Handler"),
		(r"^/hell$", "private.web.hell", "Handler"),
	)
	server = make_server("", 8080, application)
	server.serve_forever()


if __name__ == "__main__":
	main()
