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


def to_bytes(string):
	""" 文字列をバイト列に変換
	Python2の文字列型/Unicode型、Python3の文字列型に対応
	（Python2の文字列型はそのまま返し、それ以外はUTF-8にエンコードする）

	@param string: 文字列
	@return: バイト列
	"""
	if not hasattr(string, "decode"):
		# decodeメソッドがなければPython3の文字列型なのでバイト文字列にエンコードして返す
		return string.encode("utf-8")

	if type(string) != str:
		# str型でなければPython2の文字列型
		return string.encode("utf-8")

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


def hash128(data):
	""" 衝突の確率が極めて低い128bitのハッシュ値を生成
	（単なるMD5ハッシュではない）

	@param data: データを生成する文字列
	@return: ハッシュ値（バイト列）
	"""
	from hashlib import md5

	# 8回繰り返した文字列のMD5ハッシュを計算
	# （8回繰り返した文字列同士のMD5ハッシュ値が衝突する確率は極めて少ないため）
	h = md5(to_bytes(data * 8))
	return h.digest()
