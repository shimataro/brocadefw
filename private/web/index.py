# -*- coding: utf-8 -*-
""" トップページ """

from private.application import MyBaseHandler

class Handler(MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """
#		self.__test_i18n()

		template = self.create_template_html()
		return template.render("index.html")


	def __test_i18n(self):
		""" i18nモジュールの使用例 """
		from brocade.i18n import I18n

		i18n = I18n(accept_languages = self.parse_accept("Language"))
		labels = i18n.labels()
		print(i18n.message(labels.NAME))
		print(i18n.message(labels.MYNAME, {"name": "shimataro"}))
