# -*- coding: utf-8 -*-
""" hell,word """

from private.application import MyBaseHandler

class Handler(MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """
		template = self.create_template_html()
		return template.render("hell.html")
