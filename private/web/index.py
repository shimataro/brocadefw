# -*- coding: utf-8 -*-
""" トップページ """

from private import handler

class Handler(handler.MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """

		# i18nモジュールの使用例
		from brocade.i18n import I18n
		i18n = I18n()
		labels = i18n.labels()
		print(i18n.message(labels.NAME))
		print(i18n.message(labels.MYNAME, {"name": "shimataro"}))

		template = self.create_template_html()
		return template.render("index.html")
