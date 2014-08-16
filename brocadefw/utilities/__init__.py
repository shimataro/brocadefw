# -*- coding: utf-8 -*-
""" ユーティリティ関数 """

def timestamp(microsec = False):
	""" タイムスタンプを取得

	@param microsec: マイクロ秒（浮動小数点数）で取得するならTrue
	@return: タイムスタンプ
	"""
	from time import time
	result = time()
	if microsec:
		return result

	return int(result)
