# -*- coding: utf-8 -*-
""" テンプレートドライバ: Jinja2

@see: http://jinja.pocoo.org/
@see: https://pypi.python.org/pypi/Jinja2
"""

from . import BaseTemplate

class Template(BaseTemplate):
	""" テンプレートクラス """

	def __init__(self, searchpath, compile_dir, encoding_input, encoding_output, encoding_error, filter_output, params):
		""" コンストラクタ

		@param searchpath: 検索パスリスト
		@param compile_dir: コンパイル結果の保存先ディレクトリ
		@param encoding_input: 入力エンコード（ファイル）
		@param encoding_output: 出力エンコード
		@param encoding_error: 出力エンコードエラー時の対処法
		@param filter_output: 出力結果に適用するフィルタ
		@param params: テンプレートエンジンに渡すパラメータ
		@return: テンプレート検索オブジェクト
		"""
		from jinja2.environment import Environment
		from jinja2.loaders import FileSystemLoader

		super(Template, self).__init__(encoding_output, encoding_error, filter_output)

		self._env = Environment(loader = FileSystemLoader(searchpath, encoding = encoding_input))


	def render(self, filename):
		template = self._env.get_template(filename)
		data = template.render(self._vars)
		return self._output(data)
