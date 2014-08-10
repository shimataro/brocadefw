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


def validate_email(email):
	""" Eメールアドレスのフォーマットを検証

	@param email: Eメールアドレス
	@return: OK/NG
	@see: http://www.w3.org/TR/html5/forms.html#valid-e-mail-address
	"""
	import re
	pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
	regex = re.compile(pattern)
	if not regex.match(email):
		return False

	return True
