# -*- coding: utf-8 -*-
""" hell,word """

from private import handler

class Handler(handler.MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """
		template = self.create_template_html("hell.html")
		template_vars = {
			"charset": self.charset(),
		}

		return template.render(**template_vars)
