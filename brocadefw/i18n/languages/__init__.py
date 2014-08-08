# -*- coding: utf-8 -*-

def load(name):
	""" 言語モジュールをロード

	@param name: モジュール名
	@return: モジュール
	"""
	module_path = __name__.split(".")
	module_path.append(name)

	from importlib import import_module
	return import_module(".".join(module_path))
