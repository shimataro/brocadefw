# -*- coding: utf-8 -*-


class BaseTemplate(object):
	""" テンプレートのベースクラス（renderを実装すること） """

	def __init__(self, encoding_output, encoding_error, filter_output):
		self._vars = {}
		self.__encoding_output = encoding_output
		self.__encoding_error  = encoding_error
		self.__filter_output = filter_output


	def set_var(self, name, value):
		self._vars[name] = value
		return self


	def set_vars(self, data):
		self._vars.update(data)
		return self


	def render(self, filename):
		raise NotImplementedError("render")


	def _output(self, data):
		""" 入力データにフィルタを適用し、出力エンコーディングに変換

		@param data: 入力データ
		@return: 出力結果
		"""
		if self.__filter_output != None:
			data = self.__filter_output(data)

		return data.encode(self.__encoding_output, self.__encoding_error)
