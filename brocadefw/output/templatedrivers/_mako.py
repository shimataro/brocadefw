# -*- coding: utf-8 -*-
""" テンプレートドライバ: Mako

@see: http://www.makotemplates.org/
@see: https://pypi.python.org/pypi/Mako
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
		from mako.lookup import TemplateLookup

		super(Template, self).__init__()

		params_ = {
			"directories"    : searchpath,
			"input_encoding" : encoding_input,
			"output_encoding": encoding_output,
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
