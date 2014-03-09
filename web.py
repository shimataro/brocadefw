#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

def main():
	from wsgiref.simple_server import make_server
	from brocade.wsgi import middlewares

	application = middlewares.UrlMapper(
		"private.web.default",
		(r"^/$", "private.web.index"),
		(r"^/hell$", "private.web.hell"),
	)
	server = make_server("", 8080, application)
	server.serve_forever()


if __name__ == "__main__":
	main()
