# -*- coding: utf-8 -*-
""" デフォルト画面 """

from private.application import MyBaseHandler

class Handler(MyBaseHandler):
	def on_get(self):
		""" リクエスト処理 """
		return self.status_error(404)
