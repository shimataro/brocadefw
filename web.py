#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

def main():
	from wsgiref.simple_server import make_server
	from modules.wsgi import middlewares

	application = middlewares.UrlMapper(
		"web.default",
		(r"^/$", "web.index"),
		(r"^/hell$", "web.hell"),
	)
	server = make_server("", 8080, application)
	server.serve_forever()


if __name__ == "__main__":
	main()
