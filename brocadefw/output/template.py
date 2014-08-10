# -*- coding: utf-8 -*-
""" テンプレートユーティリティ """

def _import_relative_module(module_name):
	""" ここから相対位置にあるモジュールをインポート

	@param module_name: モジュール名
	@return: モジュール
	"""
	module_path = __name__.split(".")
	module_path[-1] = module_name

	from importlib import import_module
	return import_module(".".join(module_path))


def factory(driver, searchpath, compile_dir = None, encoding_input = "utf-8", encoding_output = "utf-8", params = {}):
	""" ファクトリメソッド

	@param driver: ドライバ名
	@param searchpath: 検索パスリスト
	@param compile_dir: コンパイル結果の格納場所
	@param encoding_input: 入力エンコーディング
	@param encoding_output: 出力エンコーディング
	@param param: テンプレートエンジンに渡す引数
	@return: テンプレートオブジェクト
	"""
	# "templatedrivers"以下のモジュールをロード
	module_name = "templatedrivers._{driver}".format(driver = driver)
	module = _import_relative_module(module_name)
	return module.Template(searchpath, compile_dir, encoding_input, encoding_output, params)


def get_searchpath_list(base_dir, languages = ["ja"], template_type = "html", devices = ["default"]):
	""" テンプレートの検索パスリストを取得

	@param base_dir: テンプレートファイルがあるベースディレクトリ
	@param languages: 使用する言語の順位
	@param template_type: テンプレートの種類
	@param devices: デバイスの順位（template_type="html"の場合に使用）
	@return: 検索パスリスト
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
