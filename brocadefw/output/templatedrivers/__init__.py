# -*- coding: utf-8 -*-


class BaseTemplate(object):
	""" テンプレートのベースクラス（renderを実装すること） """

	def __init__(self, encoding_output, encoding_error, filter_output):
		self._vars = {}
		self.__encoding_output = encoding_output
		self.__encoding_error  = encoding_error
		self.__filter_output = filter_output


	def set_vars(self, **kwargs):
		""" テンプレート変数を設定

		@param kwargs: 変数名・値
		"""
		self._vars.update(kwargs)
		return self


	def render(self, _filename, **kwargs):
		""" テンプレートファイルの中身を出力（本体）

		@param _filename: テンプレートファイル
		@param kwargs: 変数
		@return: 出力
		"""
		self.set_vars(**kwargs)
		return self._render(_filename)


	def _output(self, data):
		""" 入力データにフィルタを適用し、出力エンコーディングに変換

		@param data: 入力データ
		@return: 出力結果
		"""
		if self.__filter_output != None:
			data = self.__filter_output(data)

		return data.encode(self.__encoding_output, self.__encoding_error)


	def _render(self, filename):
		""" テンプレートファイルの中身を出力（本体）

		@param filename: テンプレートファイル
		@return: 出力
		"""
		raise NotImplementedError("BaseTemplate._render")
