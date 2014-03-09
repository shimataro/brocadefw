# -*- coding: utf-8 -*-
""" WSGIユーティリティ

@author: shimataro
"""

try:
	# for Py3K
	from urllib.parse import parse_qs
except ImportError:
	# for 2.X
	from urlparse import parse_qs

class Request:
	UA_DEVICES = {
		"smartphone": ["iPhone", "iPod", ("Android", "Mobile"), "dream", "CUPCAKE", "Windows Phone", "blackberry", "webOS", "incognito", "webmate"],
		"tablet": ["iPad", "Android"],
		"featurephone": ["DoCoMo", "KDDI", "DDIPOKET", "UP.Browser"," J-PHONE", "Vodafone", "SoftBank"],
	}

	""" リクエスト処理関連 """

	def __init__(self, environment):
		self.__environment = environment.copy()
		self.__cache_get  = None
		self.__cache_post = None
		self.__cache_device = None
		self.__cache_accept = {}
		self.__cache_accept_charset = {}


	def get_env(self, name, default = ""):
		""" 指定の環境変数を取得

		@param name: 変数名
		@param default: 取得できない場合のデフォルト値
		@return: 変数値またはデフォルト値
		"""
		return self.__environment.get(name, default)


	def get_request_uri(self, exclude_query = False, prepare_query = False):
		""" パスから始まる（スキームとドメインを除いた）リクエストURIを取得

		@param exclude_query: クエリストリングを取得しないならTrue
		@param prepare_query: 新たなクエリを追加できるよう、末尾に"?"または"&"を追加するならTrue
		@return: リクエストURI
		"""
		uri = self.get_env("PATH_INFO")
		has_query = False
		if not exclude_query:
			query = self.get_env("QUERY_STRING")
			if len(query) > 0:
				uri += "?" + query
				has_query = True

		if prepare_query:
			if has_query:
				uri += "&"
			else:
				uri += "?"

		return uri


	def get_remote_address(self, default = None):
		""" リモートアドレスを取得

		@param default: 取得できない場合のデフォルト値
		@return: リモートアドレス
		"""
		return self.get_env("REMOTE_ADDR", default)


	def get_user_agent(self):
		""" UAを取得

		@return: UA
		"""
		return self.get_env("HTTP_USER_AGENT")


	def device(self, smartphone = True, tablet = True, featurephone = False):
		""" UAを解析して使用デバイスを取得

		@param smartphone: スマートフォンを判別するか？
		@param tablet: タブレットを判別するか？
		@param featurephone: フィーチャーフォンを判別するか？
		@return: 判別したデバイスの文字列
		"""
		if self.__cache_device == None:
			self.__cache_device = self.__device(
				("smartphone", smartphone),
			   	("tablet", tablet),
			   	("featurephone", featurephone),
			)

		return self.__cache_device


	def parse_accept(self, name):
		""" Accept-XXXリクエストヘッダを解析

		@param key: 解析対象キー
		@return: 解析結果（受け入れ可能な情報のリスト）
		"""
		# キャッシュ調査
		key = name
		if not key in self.__cache_accept:
			self.__cache_accept[key] = self.__parse_accept(key)

		return self.__cache_accept[key]


	def charset(self, preferred = "utf-8"):
		""" Accept-Charsetリクエストヘッダを解析して最適な出力文字セットを取得

		@param preferred: デフォルトの文字セット
		@return: 出力文字セット
		"""
		# キャッシュ調査
		key = preferred
		if not key in self.__cache_accept_charset:
			self.__cache_accept_charset[key] = self.__charset(key)

		return self.__cache_accept_charset[key]


	def get(self, name = None, default = None):
		""" GETパラメータを取得 """
		# キャッシュ調査
		if self.__cache_get == None:
			self.__cache_get = self.__get()

		if name == None:
			return self.__cache_get

		return self.__cache_get.get(name, default)


	def post(self, name = None, default = None):
		""" POSTパラメータを取得 """
		# キャッシュ調査
		if self.__cache_post == None:
			self.__cache_post = self.__post()

		if name == None:
			return self.__cache_post

		return self.__cache_post.get(name, default)


	def __device(self, *args):
		""" UAを解析して使用デバイスを取得（キャッシュ不使用版）

		@param *args: ("デバイス名", [判別する/しない])のタプル
		@return: 判別したデバイス名
		"""
		user_agent = self.get_user_agent()

		for name, value in args:
			if not value:
				continue

			if not name in self.UA_DEVICES:
				continue

			for elements in self.UA_DEVICES[name]:
				if not isinstance(elements, tuple):
					elements = (elements, )

				for element in elements:
					if not element in user_agent:
						break
				else:
					return name

		return "default"


	def __parse_accept(self, name):
		""" Accept-XXXリクエストヘッダを解析（キャッシュ不使用版）

		@param key: 解析対象キー
		@return: 解析結果（受け入れ可能な情報のリスト）
		"""

		key = "HTTP_ACCEPT_" + name.upper()
		accept = self.get_env(key)
		if len(accept) == 0:
			return None

		return [piece.split(";", 2)[0].strip() for piece in accept.split(",")]


	def __charset(self, preferred):
		""" Accept-Charsetリクエストヘッダを解析して最適な出力文字セットを取得（キャッシュ不使用版）

		@param preferred: デフォルトの文字セット
		@return: 出力文字セット
		"""

		parse_result = self.parse_accept("Charset")
		if parse_result == None:
			# リクエストヘッダがない＝全ての文字コードを受け入れる＝デフォルトの文字コードを使用する
			return preferred

		charset = None
		default_charset_lower = preferred.lower()
		for element in parse_result:
			if element == "*":
				# ワイルドカードがあればデフォルトの文字コードを使用する
				return preferred

			if element.lower() == default_charset_lower:
				return preferred

			if charset == None:
				charset = element

		return charset


	def __get(self):
		""" GETパラメータを取得（キャッシュ不使用版） """
		query = self.get_env("QUERY_STRING")
		return parse_qs(query)


	def __post(self):
		""" POSTパラメータを取得（キャッシュ不使用版） """
		from modules.strutils import autodecode

		post = {}
		environment = self.__environment

		try:
			if environment["REQUEST_METHOD"] != "POST":
				return post

			wsgi_input     =     environment["wsgi.input"]
			content_length = int(environment["CONTENT_LENGTH"])
			post = parse_qs(autodecode(wsgi_input.read(content_length)))

		except:
			pass

		return post


class Response:
	""" レスポンス処理関連 """

	MIME_HTML = "text/html"
	MIME_TEXT = "text/plain"

	# HTTPステータスコード
	__status_data = {
		100: "Continue",
		101: "Switching Protocols",
		102: "Processing",

		200: "OK",
		201: "Created",
		202: "Accepted",
		203: "Non-Authoritative Information",
		204: "No Content",
		205: "Reset Content",
		206: "Partial Content",
		207: "Multi-Status",
		226: "IM Used",

		300: "Multiple Choices",
		301: "Moved Permanently",
		302: "Found",
		303: "See Other", 
		304: "Not Modified",
		305: "Use Proxy",
		306: "Unused",
		307: "Temporary Redirect",

		400: "Bad Request",
		401: "Unauthorized",
		402: "Payment Required",
		403: "Forbidden",
		404: "Not Found",
		405: "Method Not Allowed",
		406: "Not Acceptable",
		407: "Proxy Authentication Required",
		408: "Request Timeout",
		409: "Conflict",
		410: "Gone",
		411: "Length Required",
		412: "Precondition Failed",
		413: "Request Entity Too Large",
		414: "Request-URI Too Long",
		415: "Unsupported Media Type",
		416: "Requested Range Not Satisfiable",
		417: "Expectation Failed",
		418: "I'm a teapot",
		422: "Unprocessable Entity",
		423: "Locked",
		424: "Failed Dependency",
		426: "Upgrade Required",

		500: "Internal Server Error",
		501: "Not Implemented",
		502: "Bad Gateway",
		503: "Service Unavailable",
		504: "Gateway Timeout",
		505: "HTTP Version Not Supported",
		506: "Variant Also Negotiates",
		507: "Insufficient Storage",
		509: "Bandwidth Limit Exceeded",
		510: "Not Extended",
	}

	def __init__(self, request, start_response, status = 200, headers = {}, default_language = "ja"):
		self.__request = request
		self.__start_response = start_response
		self.__status = status
		self.__headers = headers
		self.__default_language = default_language


	def set_status(self, status):
		""" ステータス設定

		@param status: ステータス値
		"""
		self.__status = status


	def set_header(self, name, value):
		""" ヘッダ情報設定

		@param name: ヘッダ名
		@param value: ヘッダ値
		@param args: valueに設定する値
		"""
		self.__headers[name] = value


	def set_content_type(self, content_type):
		""" "Content-Type"ヘッダを設定 """
		if content_type in (self.MIME_HTML, self.MIME_TEXT):
			content_type += "; charset=" + self.__request.charset()

		self.set_header("Content-Type", content_type)


	def get_template_html(self, filename, status = 200):
		""" HTML用テンプレートオブジェクトを取得 """
		self.start(status)
		self.set_content_type(self.MIME_HTML)
		lookup = self.__get_template_lookup_html()
		return lookup.get_template(filename)


	def start(self, status = None):
		""" レスポンスヘッダ出力

		@param start_response: レスポンス出力関数
		"""
		if status != None:
			self.set_status(status)

		self.__start_response(self.__get_http_status(), self.__build_http_headers())


	def status_error(self, status):
		""" HTTPステータスエラー処理 """
		filename = "%s.html" % (status)
		template = self.get_template_html(filename, status)
		template_vars = {
			"charset": self.__request.charset(),
		}

		return template.render(**template_vars)


	def __get_http_status(self):
		""" HTTPステータス文字列を取得

		@return: ステータス文字列（対応する文字列がなければステータス値をそのまま返す）
		"""
		result = str(self.__status)
		description = self.__status_data.get(self.__status, "")
		if len(description) > 0:
			result += " " + description

		return result


	def __build_http_headers(self):
		""" ヘッダ情報を構築

		@return: ヘッダ情報（リスト型）
		"""
		return list(self.__headers.items())


	def __get_template_lookup(self, base_dir = "templates", cache_dir = "tmp/mako/", lookup_params = {}):
		""" テンプレート検索オブジェクトを取得

		@param base_dir: テンプレートファイルがあるベースディレクトリ
		@param cache_dir: キャッシュディレクトリ
		@param lookup_params: TemplateLookupに渡すパラメータ
		@return: テンプレート検索オブジェクト
	   	"""
		from modules.libs.mako.lookup import TemplateLookup

		# デフォルトパラメータ
		params = {
			"directories"        : self.__get_lookup_directories(base_dir),
			"input_encoding"     : "utf-8",
			"output_encoding"    : "utf-8",
			"encoding_errors"    : "replace",
			"modulename_callable": (lambda filename, uri: cache_dir + filename),
		}

		# パラメータを上書き
		params.update(lookup_params)
		return TemplateLookup(**params)


	def __get_template_lookup_html(self):
		""" HTML用テンプレート検索オブジェクトを取得

		@return: テンプレート検索オブジェクト
		"""
		from modules import minify

		return self.__get_template_lookup(
			lookup_params = {
				"output_encoding": self.__request.charset(),
				"encoding_errors": "xmlcharrefreplace",
				"preprocessor"   : minify.html
			}
		)


	def __get_lookup_directories(self, base_dir):
		""" テンプレートの検索場所一覧を取得

		@param base_dir: テンプレートファイルがあるベースディレクトリ
		@return: 検索場所一覧
		"""

		# 言語一覧
		languages = self.__request.parse_accept("Language")
		if languages == None:
			languages = []
		languages.append(self.__default_language)

		# デバイス一覧
		device = self.__request.device()
		devices = [device]
		if device != "default":
			devices.append("default")

		# ディレクトリ一覧
		directories = []
		for language in languages:
			for device in devices:
				directories.append("%s/%s/%s" % (base_dir, language, device))

		return directories
