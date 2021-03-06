# -*- coding: utf-8 -*-
""" ベースアプリケーション """

if __name__ == "__main__":
	from utilities import mimeutils, httputils
	from state     import cookie, session
	from output    import template, minify
else:
	from .utilities import mimeutils, httputils
	from .state     import cookie, session
	from .output    import template, minify


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
				return (self.__load_handler(module_name, class_name), m.groups(), m.groupdict())

		# マッチしなければデフォルトハンドラ
		return (self.__load_handler(*self.__default_handler_info), (), {})


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

	# セッションキー: トークン（CSRF対策用）
	SESSION_KEY_TOKEN = "token"

	# テンプレートドライバ
	TEMPLATE_DRIVER = "mako"

	def __init__(self, root_dir, default_language = "ja"):
		""" コンストラクタ

		@param root_dir: アプリケーションのルートディレクトリ
		@param default_language: デフォルト言語
		"""
		from wsgiref.headers import Headers
		self.__cache = {}
		self.__status = 200
		self.__headers = Headers([])
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
		try:
			request_method = self.get_request_method()
			if request_method == "GET":
				return self.on_get(*args, **kwargs)

			if request_method == "POST":
				return self.on_post(*args, **kwargs)

			if request_method == "PUT":
				return self.on_put(*args, **kwargs)

			if request_method == "PATCH":
				return self.on_patch(*args, **kwargs)

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

			if request_method == "LINK":
				return self.on_link(*args, **kwargs)

			if request_method == "UNLINK":
				return self.on_unlink(*args, **kwargs)

			return self.__error405()

		except ExitException as e:
			return e.body()


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

	def on_patch(self, *args, **kwargs):
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

	def on_link(self, *args, **kwargs):
		return self.__error405()

	def on_unlink(self, *args, **kwargs):
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
			session_id = session.generate_id()

		cookie.set(session_name, session_id, expires = lifetime, path = path, domain = domain, httponly = True)
		return session_id


	def session_storage(self):
		""" セッションストレージを取得
		（セッションを使うならオーバーライドして適切なストレージを返すこと）

		@return: セッションストレージ
		"""
		return session.Storage()


	def __session_save(self):
		""" セッション状態を保存 """
		key = "session"
		if not key in self.__cache:
			return

		session = self.__cache[key]
		session["storage"].save(session["id"], session["data"], session["lifetime"])


	########################################
	# セキュリティ
	def token_get(self):
		""" CSRF対策用のトークン取得（取得後セッションへ保存） """
		session = self.session()
		key = self.SESSION_KEY_TOKEN
		if not key in session:
			# セッションにトークンがなければ生成
			from brocadefw.utilities.randutils import gen_token
			session[key] = gen_token(as_str = True);

		return session[key]


	def token_verify(self, post_name = "token"):
		""" CSRF対策用のトークン検証

		@param post_name: トークンが入っているPOSTパラメータ名
		@return: OK/NG
		"""
		session = self.session()
		key = self.SESSION_KEY_TOKEN
		if not key in session:
			return False

		post = self.param_post()
		return post.value(post_name) == session[key]


	########################################
	# 環境情報
	def is_https(self):
		""" HTTPS通信か？

		@return: Yes/No
		"""
		return (self.get_port() == "443")


	def get_scheme(self):
		""" URIスキームを取得

		@return: URIスキーム
		"""
		if self.is_https():
			return "https"
		else:
			return "http"


	def get_root_dir(self):
		""" アプリケーションのルートディレクトリを取得

		@return: ルートディレクトリ
		"""
		return self.__root_dir


	def get_basepath(self):
		""" アプリケーションのベースパスを取得

		@return: ベースパス
		"""
		key = "basepath"
		if not key in self.__cache:
			self.__cache[key] = self._get_basepath()

		return self.__cache[key]


	def get_request_method(self):
		""" リクエストメソッドを取得

		@return: リクエストメソッド
		"""
		return self.get_env("REQUEST_METHOD").upper()


	def get_home_uri(self):
		""" ホームURIを取得

		@return: ホームURI
		"""
		return "{scheme}://{host}{basepath}".format(scheme = self.get_scheme(), host = self.get_host(), basepath = self.get_basepath())


	def get_request_uri(self, domain = False, exclude_query = False, prepare_query = False):
		""" リクエストURIを取得

		@param domain: ドメイン部を取得するならTrue
		@param exclude_query: クエリストリングを取得しないならTrue
		@param prepare_query: 新たなクエリを追加できるよう、末尾に"?"または"&"を追加するならTrue
		@return: リクエストURI
		"""
		uri = ""
		if domain:
			uri += "{scheme}://{host}".format(scheme = self.get_scheme(), host = self.get_host())

		uri += self.get_env("PATH_INFO")
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
		host = self.get_env("HTTP_HOST")
		if len(host) > 0:
			return host

		host = self.get_env("SERVER_NAME")
		port = self.get_port()
		if self.is_https():
			# HTTPSだけど443番ポートでなければポート番号も追加
			if port != "443":
				host += ":" + port
		else:
			# HTTPだけど80番ポートでなければポート番号も追加
			if port != "80":
				host += ":" + port

		return host


	def get_port(self):
		""" ポート番号を取得

		@return: ポート番号
		"""
		return self.get_env("SERVER_PORT")


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


	def parse_accept(self, name, default = None):
		""" Accept-XXXを解析して、受け入れ可能なデータをリストで取得

		@param name: XXXの部分
		@param default: 該当ヘッダがない場合のデフォルト
		@return: 解析結果
		"""
		key = "parse_accept:" + name
		if not key in self.__cache:
			self.__cache[key] = self.__parse_accept(name, default)

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


	def _get_basepath(self):
		""" アプリケーションのベースパスを取得
		* 基本的に"/"がベースパス
		* ただし、ユーザ別ディレクトリ(/~xxx/)が設定されている場合、ここをベースパスとする

		@return: ベースパス
		"""
		import re
		path = self.get_request_uri(exclude_query = True)
		match = re.match("^/(~[^/]+/)?", path)
		if match == None:
			return "/"

		return match.group(0)


	########################################
	# ヘッダ
	def set_status(self, status):
		""" ステータス設定

		@param status: ステータス
		"""
		self.__status = status


	def add_header(self, name, value, **params):
		""" ヘッダ追加

		@param name: ヘッダ名
		@param value: ヘッダ値
		@param params: ヘッダ値に '; name="value"' の形式で追加する情報があれば指定
		"""
		self.__headers.add_header(name, value, **params)


	def set_content_type(self, content_type):
		""" Content-Typeヘッダを設定

		@param content_type: コンテントタイプ
		"""
		params = {}
		if mimeutils.needs_charset(content_type):
			params["charset"] = self.charset()

		self.add_header("Content-Type", content_type, **params)


	def build_http_status(self):
		""" HTTPステータスコードを構築

		@return: ステータスコード（文字列）
		"""
		return httputils.get_status_value(self.__status)


	def build_http_headers(self):
		""" ヘッダ情報を構築

		@return: ヘッダ情報（リスト型）
		"""
		def _sanitize(name, value):
			# 改行コードを削除（ヘッダインジェクション対策）
			n = name .replace("\r", "").replace("\n", "")
			v = value.replace("\r", "").replace("\n", "")
			return (n, v)

		# ヘッダをサニタイズ
		headers = [_sanitize(name, value) for (name, value) in self.__headers.items()]

		# Cookie追加
		key = "cookie"
		if key in self.__cache:
			name = "Set-Cookie"
			headers += [_sanitize(name, value) for value in self.__cache[key].output()]

		return headers


	def redirect(self, uri, status = 302):
		""" リダイレクト

		@param uri: リダイレクト先
		@param status: ステータスコード; 301(Moved Permanently) / 302(Found) / 303(See Other) / 307(Temporary Redirect)
		"""
		self.set_status(status)
		self.add_header("Location", uri)
		raise RedirectException(uri)


	########################################
	# テンプレート
	def create_template(self, template_type, encoding_input = "utf-8", encoding_output = "utf-8", encoding_error = "replace", filter_output = None, params = {}):
		""" テンプレートオブジェクト作成
		コンパイル結果の保存先ディレクトリを指定する場合はこのメソッドをオーバーライドすること。

		@param template_type: テンプレートタイプ
		@param encoding_input: 入力エンコーディング
		@param encoding_output: 出力エンコーディング
		@param filter_output: 出力結果に適用するフィルタ
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		return self._create_template(template_type, None, encoding_input, encoding_output, encoding_error, filter_output, params)


	def create_template_html(self, status = 200, params = {}):
		""" HTML用テンプレートオブジェクト作成

		@param status: ステータスコード
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		charset = self.charset()
		template = self.create_template("html", encoding_output = charset, encoding_error = "xmlcharrefreplace", filter_output = minify.html, params = params)
		template.set_vars(charset = charset)

		# ヘッダを設定
		self.set_status(status)
		self.set_content_type(mimeutils.HTML)
		return template


	def _create_template(self, template_type, compile_dir = None, encoding_input = "utf-8", encoding_output = "utf-8", encoding_error = "replace", filter_output = None, params = {}):
		""" テンプレートオブジェクト作成の本体

		@param template_type: テンプレートタイプ
		@param compile_dir: コンパイル結果の保存先ディレクトリ
		@param encoding_input: 入力エンコーディング
		@param encoding_output: 出力エンコーディング
		@param filter_output: 出力結果に適用するフィルタ
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレートオブジェクト
		"""
		base_dir = self.get_template_basedir()

		# 言語一覧
		self.add_header("Vary", "Accept-Language")
		languages = self.get_template_languages()

		# デバイス一覧
		self.add_header("Vary", "User-Agent")
		devices = ["default"]
		user_agent = httputils.UserAgent(self.get_user_agent())
		device = user_agent.parse_device(self.get_device_info())
		if device != None:
			devices.insert(0, device)

		searchpath = template.get_searchpath_list(base_dir, languages, template_type, devices)
		return template.factory(self.TEMPLATE_DRIVER, searchpath, compile_dir, encoding_input, encoding_output, encoding_error, filter_output, params)


	def get_template_basedir(self):
		""" テンプレートのベースディレクトリを取得

		@return: ベースディレクトリ
		"""
		from os import path
		return path.join(self.get_root_dir(), "templates")


	def get_template_languages(self):
		""" テンプレート対応言語一覧を取得

		@return: 言語一覧（最後にデフォルト言語を追加）
		"""
		languages = self.parse_accept("Language")
		if languages == None:
			languages = []

		languages.append(self.__default_language)
		return languages


	def status_error(self, status):
		""" HTTPステータスエラー表示

		@param status: ステータスコード
		"""
		template = self.create_template_html(status)
		template.set_vars(
			status_code = status,
			status_name = httputils.get_status_value(status),
		)
		filename = "@http_status/{status}.html".format(status = status)
		return template.render(filename)


	def __error405(self):
		""" 405エラーを表示 """
		return self.status_error(405)


	########################################
	# キャッシュ不使用版メソッド
	def __parse_accept(self, name, default):
		""" Accept-XXXリクエストヘッダを解析（キャッシュ不使用版）

		@param name: 解析対象キー
		@param default: 該当ヘッダがない場合のデフォルト
		@return: 解析結果（受け入れ可能な情報のリスト）
		"""

		key = "HTTP_ACCEPT_" + name.upper()
		accept = self.get_env(key)
		if len(accept) == 0:
			return default

		return [piece.split(";", 2)[0].strip() for piece in accept.split(",")]


	def __charset(self, preferred):
		""" Accept-Charsetリクエストヘッダを解析して最適な出力文字セットを取得（キャッシュ不使用版）

		@param preferred: デフォルトの文字セット
		@return: 出力文字セット
		"""
		self.add_header("Vary", "Accept-Charset")
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


class ExitException(Exception):
	""" アプリケーションを終了する際に投げる例外 """
	def body(self):
		return b""


class RedirectException(ExitException):
	""" リダイレクト用の例外 """
	pass


class StatusException(ExitException):
	""" ステータスエラー用の例外 """
	def __init__(self, status, handler):
		self.__status = status
		self.__handler = handler


	def body(self):
		return self.__handler.status_error(self.__status)
