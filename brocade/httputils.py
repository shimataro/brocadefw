# -*- coding: utf-8 -*-
""" HTTPユーティリティ """

_HTTP_STATUS_DATA = {
	100: "Continue",
	101: "Switching Protocols",
	102: "Processing",

	200: "OK",
	201: "Created",
	202: "Accepted",
	203: "Non-Authoritative Information",
	204: "No Content",
	205: "Reset Content",
	206: "Partial Content",
	207: "Multi-Status",
	226: "IM Used",

	300: "Multiple Choices",
	301: "Moved Permanently",
	302: "Found",
	303: "See Other",
	304: "Not Modified",
	305: "Use Proxy",
	306: "Unused",
	307: "Temporary Redirect",

	400: "Bad Request",
	401: "Unauthorized",
	402: "Payment Required",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	406: "Not Acceptable",
	407: "Proxy Authentication Required",
	408: "Request Timeout",
	409: "Conflict",
	410: "Gone",
	411: "Length Required",
	412: "Precondition Failed",
	413: "Request Entity Too Large",
	414: "Request-URI Too Long",
	415: "Unsupported Media Type",
	416: "Requested Range Not Satisfiable",
	417: "Expectation Failed",
	418: "I'm a teapot",
	422: "Unprocessable Entity",
	423: "Locked",
	424: "Failed Dependency",
	426: "Upgrade Required",

	500: "Internal Server Error",
	501: "Not Implemented",
	502: "Bad Gateway",
	503: "Service Unavailable",
	504: "Gateway Timeout",
	505: "HTTP Version Not Supported",
	506: "Variant Also Negotiates",
	507: "Insufficient Storage",
	509: "Bandwidth Limit Exceeded",
	510: "Not Extended",
}


def get_status_value(status):
	""" HTTPステータスを取得

	@param status: ステータスコード
	@return: ステータス文字列
	"""
	result = str(status)
	description = _HTTP_STATUS_DATA.get(status, "")
	if len(description) > 0:
		result += " " + description

	return result


class UserAgent:
	""" UA解析 """

	def __init__(self, user_agent):
		""" コンストラクタ

		@param user_agent: UA
		"""
		self.__user_agent = user_agent


	def parse_device(self, device_info):
		""" UA内のデバイス情報を解析

		@param device_info: デバイス識別情報
		@return: デバイス情報（識別できなければNone）
		"""
		user_agent = self.__user_agent
		for name, keywords in device_info:
			for elements in keywords:
				if not isinstance(elements, tuple):
					elements = (elements, )

				# UAにelements内の文字列が全て含まれていればOK
				for element in elements:
					if not element in user_agent:
						break
				else:
					return name

		return None
