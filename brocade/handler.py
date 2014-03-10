# -*- coding: utf-8 -*-
""" ベースハンドラ """

# MIMEタイプ
MIME_HTML = "text/html"
MIME_TEXT = "text/plain"

# UAによるデバイスタイプ判別データ
UA_DEVICE_TYPES = {
	"smartphone"  : ["iPhone", "iPod", ("Android", "Mobile"), "dream", "CUPCAKE", "Windows Phone", "blackberry", "webOS", "incognito", "webmate"],
	"tablet"      : ["iPad", "Android"],
	"featurephone": ["DoCoMo", "KDDI", "DDIPOKET", "UP.Browser"," J-PHONE", "Vodafone", "SoftBank"],
}


def get_http_status(status):
	""" HTTPステータスを取得

	@param status: ステータスコード
	@return: ステータス文字列
	"""
	HTTP_STATUS_DATA = {
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

	result = str(status)
	description = HTTP_STATUS_DATA.get(status, "")
	if len(description) > 0:
		result += " " + description

	return result


class BaseHandler(object):
	""" リクエストハンドラクラス """

	def __init__(self, default_language = "ja"):
		""" コンストラクタ

		@param default_language: デフォルト言語
		"""
		self.__cache = {}
		self.__headers = {}
		self.__default_language = default_language


	def __call__(self, *args, **kwargs):
		""" リクエスト処理部 """
		request_method = self.get_request_method()
		if request_method == "GET":
			return self.on_get(*args, **kwargs)

		if request_method == "POST":
			return self.on_post(*args, **kwargs)

		if request_method == "PUT":
			return self.on_put(*args, **kwargs)

		if request_method == "DELETE":
			return self.on_delete(*args, **kwargs)

		if request_method == "HEAD":
			return self.on_head(*args, **kwargs)

		if request_method == "TRACE":
			return self.on_trace(*args, **kwargs)

		if request_method == "OPTIONS":
			return self.on_options(*args, **kwargs)

		if request_method == "CONNECT":
			return self.on_connect(*args, **kwargs)

		return self.__error405()


	########################################
	# ハンドラ
	def on_get(self, *args, **kwargs):
		return self.__error405()

	def on_post(self, *args, **kwargs):
		return self.__error405()

	def on_put(self, *args, **kwargs):
		return self.__error405()

	def on_delete(self, *args, **kwargs):
		return self.__error405()

	def on_head(self, *args, **kwargs):
		return self.__error405()

	def on_trace(self, *args, **kwargs):
		return self.__error405()

	def on_options(self, *args, **kwargs):
		return self.__error405()

	def on_connect(self, *args, **kwargs):
		return self.__error405()


	########################################
	# 必須実装
	def _param_get_nocache(self):
		""" GETパラメータを取得（キャッシュ不使用版） """
		raise NotImplementedError("_param_get_nocache")

	def _param_post_nocache(self):
		""" POSTパラメータを取得（キャッシュ不使用版） """
		raise NotImplementedError("_param_post_nocache")

	def get_env(self, name, default = ""):
		""" 環境変数を取得

		@param name: 変数名
		@param default: 取得出来なかった場合のデフォルト値
		@return: 環境変数
		"""
		raise NotImplementedError("get_env")

	def start(self, status = None):
		""" レスポンス開始

		@param status: ステータスコード
		"""
		raise NotImplementedError("start")


	########################################
	# パラメータ
	def param_get(self, name = None, default = None):
		""" GETパラメータを取得

		@param name: 取得するパラメータ名（省略時は全パラメータを辞書として取得）
		@param default: 取得できなかった場合のデフォルト値
		@return: 指定したパラメータ値または全パラメータ
		"""
		key = "param_get"
		if not key in self.__cache:
			self.__cache[key] = self._param_get_nocache()

		data = self.__cache[key]
		if name == None:
			return data

		return data.get(name, default)


	def param_post(self, name = None, default = None):
		""" POSTパラメータを取得

		@param name: 取得するパラメータ名（省略時は全パラメータを辞書として取得）
		@param default: 取得できなかった場合のデフォルト値
		@return: 指定したパラメータ値または全パラメータ
		"""
		key = "param_post"
		if not key in self.__cache:
			self.__cache[key] = self._param_post_nocache()

		data = self.__cache[key]
		if name == None:
			return data

		return data.get(name, default)


	########################################
	# 環境情報
	def get_request_method(self):
		""" リクエストメソッドを取得 """
		return self.get_env("REQUEST_METHOD").upper()


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


	def get_host(self):
		""" ホスト名を取得

		@return: ホスト名
		"""
		return self.get_env("HTTP_HOST")


	def get_user_agent(self):
		""" UAを取得

		@return: UA
		"""
		return self.get_env("HTTP_USER_AGENT")


	########################################
	# 解析
	def parse_device(self, smartphone = True, tablet = True, featurephone = False):
		""" UAを解析して使用デバイスを取得

		@param smartphone: スマートフォンを判別するか？
		@param tablet: タブレットを判別するか？
		@param featurephone: フィーチャーフォンを判別するか？
		@return: 判別したデバイスの文字列
		"""
		key = "parse_device:" + str(smartphone) + str(tablet) + str(featurephone)
		if not key in self.__cache:
			self.__cache[key] = self.__parse_device(
				("smartphone", smartphone),
			   	("tablet", tablet),
			   	("featurephone", featurephone),
			)

		return self.__cache[key]


	def parse_accept(self, name):
		""" Accept-XXXを解析して、受け入れ可能なデータをリストで取得

		@param name: XXXの部分
		@return: 解析結果
		"""
		key = "parse_accept:" + name
		if not key in self.__cache:
			self.__cache[key] = self.__parse_accept(name)

		return self.__cache[key]


	def charset(self, preferred = "utf-8"):
		""" Accept-Charsetリクエストヘッダを解析して最適な出力文字セットを取得

		@param preferred: デフォルトの文字セット
		@return: 出力文字セット
		"""
		key = "charset:" + preferred
		if not key in self.__cache:
			self.__cache[key] = self.__charset(preferred)

		return self.__cache[key]


	########################################
	# ヘッダ
	def set_header(self, name, value):
		""" ヘッダ情報設定

		@param name: ヘッダ名
		@param value: ヘッダ値
		"""
		self.__headers[name] = value


	def set_content_type(self, content_type):
		""" Content-Typeヘッダを設定

		@param content_type: コンテントタイプ
		"""
		if content_type in (MIME_HTML, MIME_TEXT):
			content_type += "; charset=" + self.charset()

		self.set_header("Content-Type", content_type)


	def build_http_headers(self):
		""" ヘッダ情報を構築

		@return: ヘッダ情報（リスト型）
		"""
		return list(self.__headers.items())


	########################################
	# テンプレート
	def create_template(self, filename, lookup_params = {}):
		""" テンプレートオブジェクトを作成

		@param filename: テンプレートファイル名
		@param lookup_params: TemplateLookupに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		lookup = self.__get_template_lookup_html(lookup_params)
		return lookup.get_template(filename)


	def create_template_html(self, filename, status = 200, lookup_params = {}):
		""" HTML用テンプレートオブジェクトを作成

		@param filename: テンプレートファイル名
		@param status: ステータスコード
		@param lookup_params: TemplateLookupに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		# ヘッダを出力
		self.set_content_type(MIME_HTML)
		self.start(status)
		return self.create_template(filename, lookup_params)


	def status_error(self, status):
		""" HTTPステータスエラー表示

		@param status: ステータスコード
		"""
		filename = "%s.html" % (status)
		template = self.create_template_html(filename, status)
		return template.render(charset = self.charset())


	def __error405(self):
		""" 405エラーを表示 """
		return self.status_error(405)


	########################################
	# キャッシュ不使用版メソッド
	def __parse_device(self, *args):
		""" UAを解析して使用デバイスを取得（キャッシュ不使用版）

		@param *args: ("デバイス名", [判別する/しない])のタプル
		@return: 判別したデバイス名
		"""
		user_agent = self.get_user_agent()

		for name, value in args:
			if not value:
				continue

			if not name in UA_DEVICE_TYPES:
				continue

			for elements in UA_DEVICE_TYPES[name]:
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

		@param name: 解析対象キー
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


	########################################
	# テンプレート検索
	def __get_template_lookup(self, base_dir = "templates", template_type = "html", lookup_params = {}):
		""" テンプレート検索オブジェクトを取得

		@param base_dir: テンプレートファイルがあるベースディレクトリ
		@param template_type: テンプレートの種類
		@param lookup_params: TemplateLookupに渡すパラメータ
		@return: テンプレート検索オブジェクト
	   	"""
		from brocade.libs.mako.lookup import TemplateLookup

		# デフォルトパラメータ
		params = {
			"directories"    : self.__get_lookup_directories(base_dir, template_type),
			"input_encoding" : "utf-8",
			"output_encoding": "utf-8",
			"encoding_errors": "replace",
		}

		# パラメータを上書き
		params.update(lookup_params)
		return TemplateLookup(**params)


	def __get_template_lookup_html(self, lookup_params = {}):
		""" HTML用テンプレート検索オブジェクトを取得

		@param lookup_params: TemplateLookupに渡すパラメータ
		@return: テンプレート検索オブジェクト
		"""
		from brocade import minify

		lookup_params_ = lookup_params.copy()
		lookup_params_.update({
			"output_encoding": self.charset(),
			"encoding_errors": "xmlcharrefreplace",
			"preprocessor"   : minify.html,
		})
		return self.__get_template_lookup(
			template_type = "html",
			lookup_params = lookup_params_,
		)


	def __get_lookup_directories(self, base_dir, template_type):
		""" テンプレートの検索場所一覧を取得

		@param base_dir: テンプレートファイルがあるベースディレクトリ
		@param template_type: テンプレートの種類
		@return: 検索場所一覧
		"""

		# 言語一覧
		languages = self.parse_accept("Language")
		if languages == None:
			languages = []
		languages.append(self.__default_language)

		# デバイス一覧
		device = self.parse_device()
		devices = [device]
		if device != "default":
			devices.append("default")

		# ディレクトリ一覧
		directories = []
		for language in languages:
			directory = "%s/%s/%s" % (base_dir, language, template_type)

			if template_type == "html":
				# HTMLならデバイス別ディレクトリを設定
				for device in devices:
					directories.append("%s/%s" % (directory, device))

			else:
				directories.append(directory)

		return directories
