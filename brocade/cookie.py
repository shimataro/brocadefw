# -*- coding: utf-8 -*-
""" Cookie関連 """

class CookieManager(object):
	""" Cookieマネージャ """
	
	def __init__(self, rawdata = None):
		""" コンストラクタ
		SimpleCookieオブジェクトを生成
	
		@param rawdata: クライアントから送られてきた生データ
		"""
		try:
			# >= Python 3.0
			from http import cookies as c
		except ImportError:
			# < Python 3.0
			import Cookie as c

		self.__cookie_i = c.SimpleCookie(rawdata)
		self.__cookie_o = c.SimpleCookie()


	def get(self, name, default = None):
		""" Cookie情報取得

		@param name: Cookie名（省略時はCookieオブジェクトを取得）
		@param default: Cookie名が存在しないときに返すデフォルト値
		@return: Cookie値 or SimpleCookieオブジェクト（name省略時） or default（nameがない時）
		"""
		cookie = self.__cookie_i
		# 名前が省略されたらCookieオブジェクトを返す
		if name == None:
			return cookie

		# 該当の名前がなければデフォルト値を返す
		if not name in cookie:
			return default

		# Cookie値を返す
		return cookie[name].value
	
	
	def set(self, name, value = "", expires = None, path = None, domain = None, secure = False, httponly = False):
		""" Cookie値設定

		@param name: Cookie名
		@param value: Cookie値
		@param expires: 失効日時（整数を指定した場合は自動的に文字列表現に変換され、 "Max-Age" 属性にも同じ値が設定される）
		@param path: 保存パス
		@param domain: 保存ドメイン
		@param secure: HTTPS接続のみクライアントが送信するか？
		@param httponly: HTTPのみクライアントがアクセスできるようにするか？
		"""
		cookie = self.__cookie_o
		cookie[name] = value
		if expires != None:
			cookie[name]["expires" ] = expires
			if isinstance(expires, int):
				cookie[name]["max-age" ] = expires
		if path != None:
			cookie[name]["path"    ] = path
		if domain != None:
			cookie[name]["domain"  ] = domain
		if secure:
			cookie[name]["secure"  ] = True
		if httponly:
			cookie[name]["httponly"] = True


	def delete(self, name):
		""" Cookie削除

		@param name: Cookie名
		"""
		self.set(name, expires = "Thu, 01-Jan-1970 00:00:00 GMT")


	def output(self, name = None):
		""" クライアントへ送信する形式のデータを取得

		@param name: Cookie名
		@return: Cookie値（name省略時は全てのCookie値のジェネレータ、nameが見つからない場合はNone）
		"""
		cookie = self.__cookie_o
		if name == None:
			return (morsel.OutputString() for morsel in cookie.values())

		if name in cookie:
			return cookie[name].OutputString()

		return None
