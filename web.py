#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

from brocade.wsgi import application
app = application.WSGI_Application(
	("private.web.default", "Handler"),
	(r"^/$", "private.web.index", "Handler"),
	(r"^/hell$", "private.web.hell", "Handler"),
)


def main():
	from wsgiref.simple_server import make_server
	server = make_server("", 8080, app)
	server.serve_forever()


if __name__ == "__main__":
	main()
