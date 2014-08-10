# -*- coding: utf-8 -*-


class BaseTemplate(object):
	""" テンプレートのベースクラス（renderを実装すること） """

	def __init__(self):
		self._vars = {}


	def set_var(self, name, value):
		self._vars[name] = value
		return self


	def set_vars(self, data):
		self._vars.update(data)
		return self


	def render(self, filename):
		raise NotImplementedError("render")
