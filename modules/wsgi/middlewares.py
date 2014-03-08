# -*- coding: utf-8 -*-
""" ミドルウェアモジュール

@author: shimataro
"""

class UrlMapper:
	""" URLマッピング用ミドルウェア """

	def __init__(self, default_module_name, *maps):
		""" コンストラクタ

		@param app_default: mapsのいずれにもマッチしなかった場合のデフォルトアプリケーション
		@param maps: マッピングデータ（(<正規表現パターン>, <マッチ時のインポートモジュール>)のタプル。最初のものから順に照合していく）
		"""
		import re

		maps_parsed = []
		for pattern, module_name in maps:
			pattern_c   = re.compile(pattern)
			maps_parsed.append((pattern_c, module_name))

		self.__maps_parsed         = maps_parsed
		self.__default_module_name = default_module_name


	def __call__(self, environ, start_response):
		""" リクエスト処理 """
		from . import utils
#		environ["HTTP_ACCEPT_CHARSET"] = "iso-8859-5, unicode-1-1;q=0.8"
#		environ["HTTP_ACCEPT_CHARSET"] = "Shift_JIS,utf-8;q=0.7,*;q=0.7"
		request  = utils.Request(environ)
		response = utils.Response(request, start_response)

		uri = request.get_request_uri(True)

		(module, captured) = self.__get_mapped_module(uri)
		yield module.main(request, response, *captured)


	def __get_mapped_module(self, uri):
		""" URLに対応したモジュールとキャプチャパターンを取得

		@param uri: リクエストされたURI（クエリストリングなし）
		@return: モジュールとキャプチャパターンのタプル
		"""
		from importlib import import_module
		for pattern_c, module_name in self.__maps_parsed:
			m = pattern_c.match(uri)
			if m != None:
				# マッチしたら関連モジュール
				return (import_module(module_name), m.groups())

		# マッチしなければデフォルトモジュール
		return (import_module(self.__default_module_name), ())
