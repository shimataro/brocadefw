# -*- coding: utf-8 -*-
""" デフォルト画面 """

def main(request, response):
	""" リクエスト処理 """
	return response.status_error(404)
