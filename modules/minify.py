# -*- coding: utf-8 -*-
""" ミニファイ用モジュール

@author: shimataro
"""

class _cre:
	""" コンパイル済み正規表現 """
	import re

	# 共通・改行/タブ
	common_lf    = re.compile(r"[\r\n\t]+")
	# 共通・それ以外の空白文字
	common_space = re.compile(r"\s+")

	# HTML・特殊タグ
	html_special = re.compile(r"(.*?)<(script|style|pre|textarea)\b([^>]*)>([^<]*)</\2>", re.I | re.S)
	# HTML・コメント
	html_comment = re.compile(r"<!--.*?-->", re.S)

	# CSS・コメント
	css_comment   = re.compile(r"/\*.*?\*/", re.S)
	# CSS・コロンおよび両脇の空白
	css_colon     = re.compile(r"\s*:\s*")
	# CSS・閉じカッコの前のセミコロン
	css_semicolon = re.compile(r"\s*\;\s*\}")


def html(data):
	""" HTMLをミニファイ """
	data = _html_comment(data)
	data = _html(data)
	return data


def css(data):
	""" CSSをミニファイ """
	data = _cre.css_comment  .sub("" , data)
	data = _common(data, False)
	data = _cre.css_colon    .sub(":", data)
	data = _cre.css_semicolon.sub("}", data)
	return data


def js(data):
	""" JSをミニファイ """
	# 今のところは何もしない
	return data


def _common(data, remove_lf = False):
	""" 基本的なミニファイ処理 """
	if remove_lf:
		# 改行・タブを完全に削除
		data = _cre.common_lf.sub("", data)

	# 連続するスペースを1つのスペースに置換
	data = _cre.common_space.sub(" ", data)
	return data


def _html(data):
	""" コメントを除いたHTMLをミニファイ """
	result = ""
	offset = 0
	for match in _cre.html_special.finditer(data):
		before   = match.group(1)
		tag      = match.group(2)
		attr     = match.group(3)
		contents = match.group(4)

		result += "%s<%s%s>%s</%s>" % (_common(before, True), tag, _common(attr, True), _html_special(tag, contents), tag)

		offset = match.end()

	# 残りは普通にミニファイ
	remains = data[offset:]
	result += _common(remains, True)
	return result


def _html_special(tag, data):
	""" 特殊タグの中身をミニファイ """
	tag = tag.lower()
	if tag == "script":
		return js(data)

	if tag == "style":
		return css(data)

	if tag == "pre":
		return _html_pre(data)

	if tag == "textarea":
		return _html_textarea(data)

	# ここには来ないはず
	return data


def _html_comment(data):
	""" HTMLコメントをミニファイ """
	def _html_comment_cond(match):
		comment = match.group()
		if comment.startswith("<!--[if"):
			# 条件付きコメント（はじめ）
			return comment

		if comment.endswith("<![endif]-->"):
			# 条件付きコメント（おわり）
			return comment

		# 通常のコメントなら削除
		return ""

	return _cre.html_comment.sub(_html_comment_cond, data)


def _html_pre(data):
	""" preの中身をミニファイ """
	return data


def _html_textarea(data):
	""" textareaの中身をミニファイ """
	return data
