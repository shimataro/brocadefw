# -*- coding: utf-8 -*-
""" ベースハンドラ """

from . import mime

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
		raise NotImplementedError("BaseHandler::_param_get_nocache")

	def _param_post_nocache(self):
		""" POSTパラメータを取得（キャッシュ不使用版） """
		raise NotImplementedError("BaseHandler::_param_post_nocache")

	def get_env(self, name, default = ""):
		""" 環境変数を取得

		@param name: 変数名
		@param default: 取得出来なかった場合のデフォルト値
		@return: 環境変数
		"""
		raise NotImplementedError("BaseHandler::get_env")

	def start(self, status = None):
		""" レスポンス開始

		@param status: ステータスコード
		"""
		raise NotImplementedError("BaseHandler::start")


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

		return self.__cache[key]


	def param_post(self, name = None, default = None):
		""" POSTパラメータを取得

		@param name: 取得するパラメータ名（省略時は全パラメータを辞書として取得）
		@param default: 取得できなかった場合のデフォルト値
		@return: 指定したパラメータ値または全パラメータ
		"""
		key = "param_post"
		if not key in self.__cache:
			self.__cache[key] = self._param_post_nocache()

		return self.__cache[key]


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
	def get_device_info(self):
		""" UAのデバイス情報を取得 """
		return (
			("smartphone"  , ("iPhone", "iPod", ("Android", "Mobile"), "dream", "CUPCAKE", "Windows Phone", "blackberry", "webOS", "incognito", "webmate")),
			("tablet"      , ("iPad", "Android")),
			("featurephone", ("DoCoMo", "KDDI", "DDIPOKET", "UP.Browser"," J-PHONE", "Vodafone", "SoftBank")),
		)


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
		if mime.needs_charset(content_type):
			content_type += "; charset=" + self.charset()

		self.set_header("Content-Type", content_type)


	def build_http_headers(self):
		""" ヘッダ情報を構築

		@return: ヘッダ情報（リスト型）
		"""
		return list(self.__headers.items())


	########################################
	# テンプレート
	def create_template(self, template_type, params = {}):
		""" テンプレートオブジェクトを作成

		@param filename: テンプレートファイル名
		@param template_type: テンプレートタイプ
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		from . import httputils, template

		# 言語一覧
		languages = self.parse_accept("Language")
		if languages == None:
			languages = []
		languages.append(self.__default_language)

		# デバイス一覧
		devices = ["default"]
		user_agent = httputils.UserAgent(self.get_user_agent())
		device = user_agent.parse_device(self.get_device_info())
		if device != None:
			devices.insert(0, device)

		return template.Template(
			languages = languages,
			template_type = template_type,
			devices = devices,
			params = params)


	def create_template_html(self, status = 200, params = {}):
		""" HTML用テンプレートオブジェクトを作成

		@param filename: テンプレートファイル名
		@param status: ステータスコード
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		from . import minify

		# ヘッダを出力
		self.set_content_type(mime.HTML)
		self.start(status)

		params_ = params.copy()
		params_.update({
			"output_encoding": self.charset(),
			"encoding_errors": "xmlcharrefreplace",
			"preprocessor"   : minify.html,
		})

		template = self.create_template("html", params_)
		template.set_var("charset", self.charset())
		return template


	def status_error(self, status):
		""" HTTPステータスエラー表示

		@param status: ステータスコード
		"""
		template = self.create_template_html(status)
		return template.render("_http_status/%s.html" % (status))


	def __error405(self):
		""" 405エラーを表示 """
		return self.status_error(405)


	########################################
	# キャッシュ不使用版メソッド
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


class BaseParameters(object):
	""" パラメータ処理クラス """

	def get_value(self, name, default = None):
		""" 単一のパラメータ値を取得

		@param name: パラメータ名
		@param default: デフォルトパラメータ
		@return: パラメータ値
		"""
		raise NotImplementedError("BaseParameters::get_value")


	def get_values(self, name):
		""" パラメータ値のリストを取得

		@param name: パラメータ名
		@return: パラメータ値のリスト（値がない場合は空のリスト）
		"""
		raise NotImplementedError("BaseParameters::get_values")


	def get_file(self, name):
		""" アップロードファイルを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクト
		"""
		raise NotImplementedError("BaseParameters::get_file")


	def get_files(self, name):
		""" アップロードファイルのリストを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクトのリスト
		"""
		raise NotImplementedError("BaseParameters::get_files")
