# -*- coding: utf-8 -*-
""" ベースアプリケーション """

def _load_handler(module_name, class_name):
	""" ハンドラをロード

	@param module_name: モジュール名
	@param class_name: クラス名
	@return: ハンドラクラス
	"""
	from importlib import import_module
	module = import_module(module_name)
	return getattr(module, class_name)


class BaseApplication(object):
	""" アプリケーションクラス """

	def __init__(self, default_handler_info, *maps):
		""" コンストラクタ

		@param default_handler_info: どれにもマッチしなかった場合のデフォルトハンドラ([モジュール名], [クラス名])
		@param maps: マッピングデータ([正規表現], [モジュール名], [クラス名])
		"""
		import re
		maps_parsed = []
		for pattern, module_name, class_name in maps:
			pattern_c   = re.compile(pattern)
			maps_parsed.append((pattern_c, module_name, class_name))

		self.__maps_parsed          = maps_parsed
		self.__default_handler_info = default_handler_info


	def _get_matched_data(self, uri):
		""" URLにマッチしたハンドラとキャプチャパターンを取得

		@param uri: リクエストされたURI（クエリストリングなし）
		@return: ハンドラとキャプチャパターンのタプル
		"""
		for pattern_c, module_name, class_name in self.__maps_parsed:
			m = pattern_c.match(uri)
			if m != None:
				# マッチしたら対応ハンドラ
				return (_load_handler(module_name, class_name), m.groups())

		# マッチしなければデフォルトハンドラ
		return (_load_handler(*self.__default_handler_info), ())
