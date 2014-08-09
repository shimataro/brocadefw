# -*- coding: utf-8 -*-
""" テンプレートユーティリティ """

def get_lookup_directories(base_dir, languages, template_type, devices):
	""" テンプレートの検索場所一覧を取得

	@param base_dir: テンプレートファイルがあるベースディレクトリ
	@param languages: 使用する言語の順位
	@param template_type: テンプレートの種類
	@param devices: デバイスの順位（template_type="html"の場合に使用）
	@return: 検索場所一覧
	"""
	from os.path import join
	directories = []
	for language in languages:
		directory = join(base_dir, language, template_type)

		if template_type == "html":
			# HTMLならデバイス別ディレクトリを設定
			for device in devices:
				directories.append(join(directory, device))

		else:
			directories.append(directory)

	return directories


class BaseTemplate(object):
	""" テンプレートのベースクラス（renderを実装すること） """

	def __init__(self):
		self._vars = {}


	def set_var(self, name, value):
		self._vars[name] = value
		return self


	def set_vars(self, data):
		self._vars.update(data)
		return self


	def render(self, filename):
		raise NotImplementedError("render")


class Template(BaseTemplate):
	""" テンプレートクラス """

	def __init__(self, base_dir, compile_dir = None, languages = ["ja"], template_type = "html", devices = ["default"], params = {}):
		""" コンストラクタ

		@param base_dir: テンプレートファイルがあるベースディレクトリ
		@param compile_dir: コンパイル結果の保存先ディレクトリ
		@param languages: 使用する言語の順位
		@param template_type: テンプレートの種類
		@param devices: デバイスの順位（template_type="html"の場合に使用）
		@param params: テンプレートライブラリに渡すパラメータ
		@return: テンプレート検索オブジェクト
		"""
		from mako.lookup import TemplateLookup

		super(Template, self).__init__()

		params_ = {
			"directories"    : get_lookup_directories(base_dir, languages, template_type, devices),
			"input_encoding" : "utf-8",
			"output_encoding": "utf-8",
			"encoding_errors": "replace",
		}

		if compile_dir != None:
			from hashlib import md5
			from os.path import join
			params_["modulename_callable"] = lambda filename, uri: join(compile_dir, md5(filename.encode()).hexdigest() + ".py")

		params_.update(params)

		self.__lookup = TemplateLookup(**params_)


	def render(self, filename):
		return self.__lookup.get_template(filename).render(**self._vars)
