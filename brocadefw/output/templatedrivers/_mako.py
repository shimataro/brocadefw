# -*- coding: utf-8 -*-
""" テンプレートドライバ: Mako

@see: http://www.makotemplates.org/
@see: https://pypi.python.org/pypi/Mako
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
		from mako.lookup import TemplateLookup

		super(Template, self).__init__(encoding_output, encoding_error, filter_output)

		params_ = {
			"directories"    : searchpath,
			"input_encoding" : encoding_input,
			"output_encoding": encoding_output,
			"encoding_errors": encoding_error,
		}

		if compile_dir != None:
			from hashlib import md5
			from os.path import join
			params_["modulename_callable"] = lambda filename, uri: join(compile_dir, md5(filename.encode()).hexdigest() + ".py")

		params_.update(params)

		self.__lookup = TemplateLookup(**params_)


	def _render(self, filename):
		template = self.__lookup.get_template(filename)
		data = template.render_unicode(**self._vars)
		return self._output(data)
