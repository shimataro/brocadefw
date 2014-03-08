# -*- coding: utf-8 -*-
""" 文字列処理ユーティリティ

@author: shimataro
"""

def autodecode(string, encodings = ("utf-8", "shift_jis", "euc_jp", "iso2022_jp")):
	""" 文字コードを自動判別してデコード """
	for encoding in encodings:
		try:
			# 片っ端からデコードしていく
			return string.decode(encoding)

		except UnicodeDecodeError:
			# エラーが出たら次へ
			pass

	# どれでもデコードできなければ元の文字列をそのまま返す
	return string
