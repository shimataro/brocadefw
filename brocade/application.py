# -*- coding: utf-8 -*-
""" ベースアプリケーション """

from brocade.utilities import mimeutils, httputils


class BaseApplication(object):
	""" アプリケーションクラス """

	def __init__(self, root_dir, default_handler_info, *maps):
		""" コンストラクタ

		@param root_dir: アプリケーションのルートディレクトリ
		@param default_handler_info: どれにもマッチしなかった場合のデフォルトハンドラ([モジュール名], [クラス名])
		@param maps: マッピングデータ([正規表現], [モジュール名], [クラス名])
		"""
		import re
		maps_parsed = []
		for pattern, module_name, class_name in maps:
			pattern_c   = re.compile(pattern)
			maps_parsed.append((pattern_c, module_name, class_name))

		self.__maps_parsed          = maps_parsed
		self.__root_dir             = root_dir
		self.__default_handler_info = default_handler_info


	def test_run(self, host = "", port = 8080):
		""" テスト用サーバを起動（本番環境で使用しないこと）

		@param host: ホスト名
		@param port: 待機ポート
		"""
		raise NotImplementedError("BaseApplication::test_run")


	def get_root_dir(self):
		""" アプリケーションのルートディレクトリを取得

		@return: ルートディレクトリ
		"""
		return self.__root_dir


	def _get_matched_data(self, uri):
		""" URLにマッチしたハンドラとキャプチャパターンを取得

		@param uri: リクエストされたURI（クエリストリングなし）
		@return: ハンドラとキャプチャパターンのタプル
		"""
		for pattern_c, module_name, class_name in self.__maps_parsed:
			m = pattern_c.match(uri)
			if m != None:
				# マッチしたら対応ハンドラ
				return (self.__load_handler(module_name, class_name), m.groups())

		# マッチしなければデフォルトハンドラ
		return (self.__load_handler(*self.__default_handler_info), ())


	@staticmethod
	def __load_handler(module_name, class_name):
		""" ハンドラをロード

		@param module_name: モジュール名
		@param class_name: クラス名
		@return: ハンドラクラス
		"""
		from importlib import import_module
		module = import_module(module_name)
		return getattr(module, class_name)


class BaseHandler(object):
	""" リクエストハンドラクラス """

	def __init__(self, root_dir, default_language = "ja"):
		""" コンストラクタ

		@param root_dir: アプリケーションのルートディレクトリ
		@param default_language: デフォルト言語
		"""
		self.__cache = {}
		self.__status = 200
		self.__headers = {}
		self.__root_dir = root_dir
		self.__default_language = default_language


	def __call__(self, *args, **kwargs):
		""" リクエスト処理部 """
		result = self.__call(*args, **kwargs)
		self.output_headers()
		self.post_request()
		return result


	def __call(self, *args, **kwargs):
		""" リクエスト処理部の本体 """
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


	def post_request(self):
		""" リクエスト処理後に呼び出される """
		self.__session_save()


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
	def _param_get(self):
		""" GETパラメータを取得 """
		raise NotImplementedError("BaseHandler::_param_get")

	def _param_post(self):
		""" POSTパラメータを取得 """
		raise NotImplementedError("BaseHandler::_param_post")

	def get_env(self, name, default = ""):
		""" 環境変数を取得

		@param name: 変数名
		@param default: 取得出来なかった場合のデフォルト値
		@return: 環境変数
		"""
		raise NotImplementedError("BaseHandler::get_env")

	def output_headers(self):
		""" ヘッダ出力 """
		raise NotImplementedError("BaseHandler::output_headers")


	########################################
	# パラメータ
	def param_get(self):
		""" GETパラメータを取得

		@return: パラメータオブジェクト
		"""
		key = "param_get"
		if not key in self.__cache:
			self.__cache[key] = self._param_get()

		return self.__cache[key]


	def param_post(self):
		""" POSTパラメータを取得

		@return: パラメータオブジェクト
		"""
		key = "param_post"
		if not key in self.__cache:
			self.__cache[key] = self._param_post()

		return self.__cache[key]


	########################################
	# 状態管理
	def cookie(self):
		""" Cookie情報取得

		@return: Cookieマネージャ
		"""
		key = "cookie"
		if not key in self.__cache:
			from brocade.state import cookie
			self.__cache[key] = cookie.CookieManager(self.get_raw_cookie())

		return self.__cache[key]


	def session(self, session_name = "session", lifetime = 24 * 60 * 60, path = "/", domain = None):
		""" セッションデータを取得

		@param session_name: セッション名
		@param lifetime: セッションの有効期間[sec]
		@param path: パス名
		@param domain: ドメイン名
		@return: セッションデータ（辞書）
		"""
		key = "session"
		if not key in self.__cache:
			session_id = self.session_id(session_name, lifetime, path, domain)
			storage = self.session_storage();
			self.__cache[key] = {
				"id": session_id,
				"lifetime": lifetime,
				"data": storage.load(session_id),
				"storage": storage,
			}

		return self.__cache[key]["data"]


	def session_id(self, session_name, lifetime, path, domain):
		""" セッションIDを取得

		@param session_name: セッション名
		@param lifetime: セッションの有効期間[sec]
		@param path: パス名
		@param domain: ドメイン名
		@return: セッションID
		"""
		# セッションIDをCookieから取得
		cookie = self.cookie()
		session_id = cookie.get(session_name)
		if session_id == None:
			# Cookieに保存されていなければ生成
			from brocade.state import session
			session_id = session.generate_id()

		cookie.set(session_name, session_id, expires = lifetime, path = path, domain = domain, httponly = True)
		return session_id


	def session_storage(self):
		""" セッションストレージを取得
		（セッションを使うならオーバーライドして適切なストレージを返すこと）

		@return: セッションストレージ
		"""
		from brocade.state import session
		return session.Storage()


	def __session_save(self):
		""" セッション状態を保存 """
		key = "session"
		if not key in self.__cache:
			return

		session = self.__cache[key]
		session["storage"].save(session["id"], session["data"], session["lifetime"])


	########################################
	# 環境情報
	def get_root_dir(self):
		""" アプリケーションのルートディレクトリを取得

		@return: ルートディレクトリ
		"""
		return self.__root_dir


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


	def get_raw_cookie(self):
		""" 生のCookieデータを取得

		@return: Cookieデータ
		"""
		return self.get_env("HTTP_COOKIE")


	########################################
	# 解析
	def get_device_info(self):
		""" UAのデバイス情報を取得 """
		return (
			("smartphone"  , ("iPhone", "iPod", ("Android", "Mobile"), "dream", "CUPCAKE", "Windows Phone", "blackberry", "webOS", "incognito", "webmate")),
			("tablet"      , ("iPad", "Android")),
			("featurephone", ("DoCoMo", "KDDI", "DDIPOKET", "UP.Browser"," J-PHONE", "Vodafone", "SoftBank")),
		)


	def parse_accept(self, name, vary = False):
		""" Accept-XXXを解析して、受け入れ可能なデータをリストで取得

		@param name: XXXの部分
		@param vary: "Vary"ヘッダに追加するならTrue
		@return: 解析結果
		"""
		key = "parse_accept:" + name
		if not key in self.__cache:
			self.__cache[key] = self.__parse_accept(name, vary)

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
	def set_status(self, status):
		""" ステータス設定

		@param status: ステータス
		"""
		self.__status = status


	def set_header(self, name, value, append = False):
		""" ヘッダ情報設定

		@param name: ヘッダ名
		@param value: ヘッダ値
		@param append: 同名のヘッダがすでに設定されている場合にvalueを追加するならTrue
		"""
		if (name in self.__headers) and append:
			self.__headers[name] += "," + value
			return

		self.__headers[name] = value


	def set_content_type(self, content_type):
		""" Content-Typeヘッダを設定

		@param content_type: コンテントタイプ
		"""
		if mimeutils.needs_charset(content_type):
			content_type += "; charset=" + self.charset()

		self.set_header("Content-Type", content_type)


	def build_http_status(self):
		return httputils.get_status_value(self.__status)


	def build_http_headers(self):
		""" ヘッダ情報を構築

		@return: ヘッダ情報（リスト型）
		"""
		headers = list(self.__headers.items())

		# Cookie追加
		key = "cookie"
		if key in self.__cache:
			headers.extend(("Set-Cookie", data) for data in self.__cache[key].output())

		return headers


	########################################
	# テンプレート
	def create_template(self, template_type, params = {}):
		""" テンプレートオブジェクトを作成

		@param filename: テンプレートファイル名
		@param template_type: テンプレートタイプ
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		from brocade.output import template

		# 言語一覧
		languages = self.parse_accept("Language", True)
		if languages == None:
			languages = []
		languages.append(self.__default_language)

		# デバイス一覧
		self.set_header("Vary", "User-Agent", True)
		devices = ["default"]
		user_agent = httputils.UserAgent(self.get_user_agent())
		device = user_agent.parse_device(self.get_device_info())
		if device != None:
			devices.insert(0, device)

		return template.Template(
			root_dir = self.get_root_dir(),
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
		from brocade.output import minify

		params_ = params.copy()
		params_.update({
			"output_encoding": self.charset(),
			"encoding_errors": "xmlcharrefreplace",
			"preprocessor"   : minify.html,
		})

		template = self.create_template("html", params_)
		template.set_var("charset", self.charset())

		# ヘッダを設定
		self.set_status(status)
		self.set_content_type(mimeutils.HTML)
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
	def __parse_accept(self, name, vary = False):
		""" Accept-XXXリクエストヘッダを解析（キャッシュ不使用版）

		@param name: 解析対象キー
		@param vary: "Vary"ヘッダに追加するならTrue
		@return: 解析結果（受け入れ可能な情報のリスト）
		"""

		if vary:
			self.set_header("Vary", "Accept-" + name, True)

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
		parse_result = self.parse_accept("Charset", True)
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

	def value(self, name, default = None):
		""" パラメータ値を取得

		@param name: パラメータ名
		@param default: デフォルトパラメータ
		@return: パラメータ値
		"""
		raise NotImplementedError("BaseParameters::value")


	def values(self, name):
		""" パラメータ値のリストを取得

		@param name: パラメータ名
		@return: パラメータ値のリスト
		"""
		raise NotImplementedError("BaseParameters::values")


	def file(self, name):
		""" アップロードファイルを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクト
		"""
		raise NotImplementedError("BaseParameters::file")


	def files(self, name):
		""" アップロードファイルのリストを取得

		@param name: パラメータ名
		@return: filename, fileを属性に持つオブジェクトのリスト
		"""
		raise NotImplementedError("BaseParameters::files")
