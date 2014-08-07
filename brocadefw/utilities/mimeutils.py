# -*- coding: utf-8 -*-
""" MIMEタイプ """

TEXT  = "text/plain"
HTML  = "text/html"
CSS   = "text/css"
JS    = "application/javascript"
XML   = "application/xml"
XHTML = "application/xhtml+xml"
JSON  = "application/json"
SVG   = "image/svg+xml"

def needs_charset(mime_type):
	""" charset指定が必要なMIMEタイプか？ """
	return mime_type in (TEXT, HTML)
