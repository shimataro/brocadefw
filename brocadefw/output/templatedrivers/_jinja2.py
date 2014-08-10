# -*- coding: utf-8 -*-
""" テンプレートドライバ: Jinja2

@see: http://jinja.pocoo.org/
@see: https://pypi.python.org/pypi/Jinja2
"""

from . import BaseTemplate

class Template(BaseTemplate):
	""" テンプレートクラス """

	def __init__(self, searchpath, compile_dir = None, encoding_input = "utf-8", encoding_output = "utf-8", params = {}):
		""" コンストラクタ

		@param searchpath: 検索パスリスト
		@param compile_dir: コンパイル結果の保存先ディレクトリ
		@param params: テンプレートエンジンに渡すパラメータ
		@return: テンプレート検索オブジェクト
		"""
		from jinja2.environment import Environment
		from jinja2.loaders import FileSystemLoader

		super(Template, self).__init__()

		self._env = Environment(loader = FileSystemLoader(searchpath, encoding = encoding_input))
		self._encoding_output = encoding_output


	def render(self, filename):
		template = self._env.get_template(filename)
		return template.render(self._vars).encode(self._encoding_output)
