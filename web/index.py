# -*- coding: utf-8 -*-
""" トップページ """

def main(request, response):
	""" リクエスト処理 """
	template = response.get_template_html("index.html")
	template_vars = {
		"charset": request.charset(),
	}

	return template.render(**template_vars)
