#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

import private
app = private.create_application()


def main():
	from wsgiref.simple_server import make_server
	server = make_server("", 8080, app)
	server.serve_forever()


if __name__ == "__main__":
	main()
