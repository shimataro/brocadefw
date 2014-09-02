# -*- coding: utf-8 -*-
""" 乱数関連のユーティリティ """

def gen_code(columns = 4):
	""" 指定桁数のランダムな英数字コードを生成
	（0/O, 1/I/l, 2/Z, 5/S はフォントによっては紛らわしいので生成コードに含めない）

	@param columns: 生成する桁数; 省略時は4桁
	@return: コード
	"""
	import random
	chars = "346789ABCDEFGHJKLMNPQRTUVWXYabcdefghijkmnopqrstuvwxyz"
	code = ""
	for i in range(columns):
		code += random.choice(chars)

	return code


def gen_token(bits = 128, as_str = False):
	""" ランダムなトークンを生成

	@param bits: トークンのビット数: 128（16バイト/32文字）, 160（20バイト/40文字）, 256（32バイト/64文字）, 512（64バイト/128文字）
	@param as_str: 16進文字列で取得する場合はTrue
	@return: 文字列
	"""
	return _gen_hash(_hashobj(bits), as_str)


def _hashobj(bits):
	""" ハッシュオブジェクトを取得

	@param bits: ビット数
	@return: ハッシュオブジェクト
	"""
	import hashlib
	if bits == 128:
		return hashlib.md5

	if bits == 160:
		return hashlib.sha1

	if bits == 256:
		return hashlib.sha256

	if bits == 512:
		return hashlib.sha512

	raise ValueError("token bits error: %s" % bits)


def _gen_hash(hashobj, as_str):
	""" ランダムなバイト文字列にハッシュ関数を適用

	@param hashobj: ハッシュオブジェクト
	@param as_str: 16進文字列で取得する場合はTrue
	@return: 文字列
	"""
	h = hashobj(_gen_seed())
	if as_str:
		return h.hexdigest()

	else:
		return h.digest()


def _gen_seed():
	""" ランダムなバイト文字列を生成
	桁数は不定なので、必要に応じてハッシュ関数を適用すること

	@return: バイト文字列
	"""
	from os import urandom
	from time import time

	seed  = urandom(64)
	seed += str(time()).encode()
	return seed


def _test():
	""" テスト """
	print(gen_token(128, True))
	print(gen_token(160, True))
	print(gen_token(256, True))
	print(gen_token(512, True))


if __name__ == "__main__":
	_test()
