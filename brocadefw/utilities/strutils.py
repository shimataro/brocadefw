# -*- coding: utf-8 -*-
""" 文字列処理ユーティリティ

単に「文字列」と言った場合はUnicodeかバイト列か紛らわしいので、ここでは明確に区別する必要がある場合は以下のように統一する
* Unicode: Python2のunicode型 または Python3のstr型
* バイト列: Python2のstr型 または Python3のbytes型 または bytearray型

@author: shimataro
"""

def autodecode(string, encodings = ("utf-8", "shift_jis", "euc_jp", "iso2022_jp")):
	""" 文字コードを自動判別してデコード

	@param string: バイト列
	@param encodings: エンコード一覧
	@return: デコード後のUnicode文字列 or None（失敗した場合）
	"""
	for encoding in encodings:
		try:
			# 片っ端からデコードしていく
			return string.decode(encoding)

		except UnicodeDecodeError:
			# エラーが出たら次へ
			pass

	# どれでもデコードできなければNone
	return None


def is_unicode(data):
	""" Unicodeか？

	@param data: チェックする文字列
	@return: Yes/No
	"""
	t = type(data)
	try:
		# Python2
		return t == unicode

	except NameError:
		# Python3
		return t == str


def is_bytes(data):
	""" バイト列か？

	@param data: チェックするデータ
	@return: Yes/No
	"""
	t = type(data)
	if t == bytearray:
		return True

	try:
		# Python2
		return t != unicode and t == str

	except NameError:
		# Python3
		return t == bytes


def to_unicode(string, encoding = "utf-8"):
	""" 文字列をUnicodeに変換
	* Unicodeはそのまま返す
	* それ以外はデコードする

	@param string: 文字列; Unicodeまたはバイト列
	@param encoding: Unicodeでない場合のデコード方法
	@return: Unicode文字列
	"""
	if is_unicode(string):
		# Unicodeならそのまま返す
		return string

	# そうでなければデコード
	return string.decode(encoding)


def to_bytes(string, encoding = "utf-8"):
	""" 文字列をバイト列に変換
	* バイト列はそのまま返す
	* それ以外はエンコードする

	@param string: 文字列; Unicodeまたはバイト列
	@param encoding: バイト列でない場合のエンコード方法
	@return: バイト列
	"""
	if is_bytes(string):
		# バイト列ならそのまま返す
		return string

	# そうでなければエンコード
	return string.encode(encoding)


def validate_email(email):
	""" Eメールアドレスのフォーマットを検証
	* 検証するのはフォーマットのみ（アドレスが存在するかどうかを調べるわけではない）
	* RFCに厳密に従っているかをチェックするわけではない（ドットの扱い等でinvalidなものを通すことがある）

	@param email: Eメールアドレス
	@return: OK/NG
	@see: http://www.w3.org/TR/html5/forms.html#valid-e-mail-address
	"""
	import re
	pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
	return re.match(pattern, email) != None


def hash128(data):
	""" 衝突の確率が極めて低い128bitのハッシュ値を生成
	（単なるMD5ハッシュではない）

	@param data: データを生成する文字列
	@return: ハッシュ値（バイト列）
	"""
	from hashlib import md5

	# 8回繰り返した文字列のMD5ハッシュを計算
	# （8回繰り返した文字列同士のMD5ハッシュ値が衝突する確率は、繰り返さない文字列に比べて極めて低い）
	return md5(to_bytes(data) * 8).digest()


def _test():
	""" テスト """
	print("test")

	""" is_unicode/is_bytes/to_unicode/to_bytes """
	try:
		unicode
		print("Python2")

		# unicode（本当は u"xxx" とやりたいけどPython3でエラーが。。。）
		string = "(╹ω╹๑ )".decode("utf-8")
		assert is_unicode(string)
		assert not is_bytes(string)
		assert type(to_unicode(string)) == unicode
		assert type(to_bytes  (string)) == str

		# str
		string = "(๑╹ڡ╹๑)"
		assert not is_unicode(string)
		assert is_bytes(string)
		assert type(to_unicode(string)) == unicode
		assert type(to_bytes  (string)) == str

	except NameError:
		print("Python3")

		# str
		string = "ʕº̫͡ºʔ"
		assert is_unicode(string)
		assert not is_bytes(string)
		assert type(to_unicode(string)) == str
		assert type(to_bytes  (string)) == bytes

		# bytes
		string = "(;☉ฺд☉ฺ)".encode("utf-8")
		assert not is_unicode(string)
		assert is_bytes(string)
		assert type(to_unicode(string)) == str
		assert type(to_bytes  (string)) == bytes


	""" validate_email """
	email = "user"
	assert not validate_email(email)

	email = "user@"
	assert not validate_email(email)

	email = "user@example"
	assert validate_email(email)

	email = "user@example."
	assert not validate_email(email)

	email = "user@example.com"
	assert validate_email(email)

	email = "user+user2@example.com"
	assert validate_email(email)

	print("OK")


if __name__ == "__main__":
	_test()
