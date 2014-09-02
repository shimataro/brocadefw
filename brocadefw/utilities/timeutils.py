# -*- coding: utf-8 -*-
""" 時刻関連のユーティリティ """

# 時刻のフォーマット
FORMAT_RFC3339 = "%FT%T+0000"
FORMAT_RFC2822 = "%a, %d %b %Y %T +0000"
FORMAT_RFC822  = "%a, %d %b %y %T +0000"


def unixtime(microsec = False):
	""" Unixタイムスタンプを取得

	@param microsec: マイクロ秒（浮動小数点数）で取得するならTrue
	@return: Unixタイムスタンプ
	"""
	from time import time
	t = time()
	if microsec:
		return t

	return int(t)


def format_unixtime(format = FORMAT_RFC2822, timestamp = None):
	""" Unixタイムスタンプをフォーマッティング

	@param format: フォーマット文字列; strftime()の書式またはFORMAT_RFCxxx
	@param timestamp: Unixタイムスタンプ; 省略時は現在時刻
	@return: フォーマット後の時刻
	@requires: pytz
	"""
	from datetime import datetime
	import pytz
	if timestamp == None:
		timestamp = unixtime()

	return datetime.fromtimestamp(timestamp, tz = pytz.utc).strftime(format)


def _test():
	""" テスト """
	print(format_unixtime())
	print(format_unixtime(FORMAT_RFC822))
	print(format_unixtime(FORMAT_RFC3339))


if __name__ == "__main__":
	_test()
