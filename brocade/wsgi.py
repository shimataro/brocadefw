# -*- coding: utf-8 -*-
""" WSGIユーティリティ """

from brocade import handler, application


class WSGI_Handler(handler.BaseHandler):
	""" リクエストハンドラ（WSGI版） """

	def __init__(self, environ, start_response, default_language = "ja"):
		super(WSGI_Handler, self).__init__(default_language)

		# 引数
		self.__environ        = environ.copy()
		self.__start_response = start_response


	def _param_get(self):
		""" GETパラメータを取得 """
		return self.__param(False)


	def _param_post(self):
		""" POSTパラメータを取得 """
		return self.__param(True)


	def __param(self, post = False):
		""" パラメータを取得

		@param post: GETデータを取得するならFalse, POSTデータを取得するならTrue
		@return: FieldStorage
		"""
		import cgi

		fp = None
		environ = self.__environ
		keep_blank_values = True

		if post:
			# POSTならクエリ文字列をクリア
			environ = environ.copy()
			environ["QUERY_STRING"] = ""
			if "wsgi.input" in environ:
				fp = environ["wsgi.input"]

		field_storage = cgi.FieldStorage(fp = fp, environ = environ, keep_blank_values = keep_blank_values)
		return WSGI_Parameters(field_storage)


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
		from . import httputils
		self.__start_response(httputils.get_status_value(status), self.build_http_headers())


class WSGI_Parameters(handler.BaseParameters):
	""" パラメータ（WSGI版） """

	def __init__(self, field_storage):
		self.__field_storage = field_storage


	def value(self, name, default = None):
		""" 単一のパラメータ値を取得

		@param name: パラメータ名
		@param default: デフォルトパラメータ
		@return: パラメータ値
		"""
		return self.__field_storage.getfirst(name, default)


	def values(self, name):
		""" パラメータ値のリストを取得

		@param name: パラメータ名
		@return: パラメータ値のリスト（値がない場合は空のリスト）
		"""
		return self.__field_storage.getlist(name)


	def file(self, name):
		""" アップロードファイルを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクト
		"""
		field_storage = self.__field_storage
		if not name in field_storage:
			return None

		f = field_storage[name]
		if isinstance(f, list):
			f = f[0]

		if not self.__is_file(f):
			return None

		return f


	def files(self, name):
		""" アップロードファイルのリストを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクトのリスト
		"""
		field_storage = self.__field_storage
		if not name in field_storage:
			return []

		files = field_storage[name]
		if not isinstance(files, list):
			files = [files]

		if not self.__is_file(files[0]):
			return []

		return files


	@staticmethod
	def __is_file(f):
		""" 引数がファイルか？

		@param f: チェックする引数
		@return: Yes/No
		"""
		if not hasattr(f, "filename"):
			return False
		if not hasattr(f, "file"):
			return False

		if f.file == None:
			return False

		return True


class WSGI_Application(application.BaseApplication):
	""" アプリケーション（WSGI版） """

	def __call__(self, environ, start_response):
		""" リクエスト処理 """
#		environ["HTTP_ACCEPT_CHARSET"] = "iso-8859-5, unicode-1-1;q=0.8"
#		environ["HTTP_ACCEPT_CHARSET"] = "Shift_JIS,utf-8;q=0.7,*;q=0.7"

		uri = environ.get("PATH_INFO", "")

		(handler, args) = self._get_matched_data(uri)
		handler_instance = handler(environ, start_response)
		yield handler_instance(*args)
