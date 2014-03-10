# -*- coding: utf-8 -*-
""" リクエストハンドラ（WSGI版） """

from brocade import handler

try:
	# for Py3K
	from urllib.parse import parse_qs
except ImportError:
	# for 2.X
	from urlparse import parse_qs


class WSGI_Handler(handler.BaseHandler):
	""" リクエストハンドラ """

	def __init__(self, environ, start_response, default_language = "ja"):
		super(WSGI_Handler, self).__init__(default_language)

		# 引数
		self.__environ        = environ.copy()
		self.__start_response = start_response


	def _param_get_nocache(self):
		""" GETパラメータを取得（キャッシュ不使用版） """
		query = self.get_env("QUERY_STRING")
		return parse_qs(query)


	def _param_post_nocache(self):
		""" POSTパラメータを取得（キャッシュ不使用版） """
		from brocade.strutils import autodecode

		post = {}
		environ = self.__environ

		if self.get_request_method() != "POST":
			return post

		try:
			wsgi_input     =     environ["wsgi.input"]
			content_length = int(environ["CONTENT_LENGTH"])
			post = parse_qs(autodecode(wsgi_input.read(content_length)))

		except:
			pass

		return post


	def get_env(self, name, default = ""):
		""" 指定の環境変数を取得

		@param name: 変数名
		@param default: 取得できない場合のデフォルト値
		@return: 変数値またはデフォルト値
		"""
		return self.__environ.get(name, default)


	def start(self, status = 200):
		""" レスポンスヘッダ出力

		@param status: ステータス
		"""
		self.__start_response(handler.get_http_status(status), self.build_http_headers())
