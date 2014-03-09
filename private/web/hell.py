# -*- coding: utf-8 -*-
""" hell,word """

def main(request, response):
	""" リクエスト処理 """
	template = response.get_template_html("hell.html")
	template_vars = {
		"charset": request.charset(),
	}

	return template.render(**template_vars)
