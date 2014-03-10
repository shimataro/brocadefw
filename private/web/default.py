# -*- coding: utf-8 -*-
""" デフォルト画面 """

from private import handler

class Handler(handler.MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """
		return self.status_error(404)
