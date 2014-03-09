# -*- coding: utf-8 -*-
"""
XML関連のユーティリティライブラリ

@author: shimataro
"""

def escape(data, apos = False, quote = False):
	""" メタ文字をエスケープ

	@param data: エスケープする文字列
	@param apos: シングルクォートをエスケープするか？
	@param quote: 文字列全体をクォートするか？（属性値をエスケープするときに有用）
	@return: エスケープ後の文字列
	"""

	# 最初に"&"をエスケープ
	data = data.replace('&', '&amp;')
	data = data.replace('<', '&lt;')
	data = data.replace('>', '&gt;')
	data = data.replace('"', '&quot;')
	
	if apos:
		data = data.replace("'", '&apos;')

	if quote:
		data = '"%s"' % (data)

	return data


class XmlElement:
	""" XML要素クラス """

	################################################################################
	# static
	
	@staticmethod
	def create(tag, attr = {}, *children):
		""" タグ要素を作成

		@param tag: タグ文字列
		@param attr: 属性情報（name:valueの辞書）
		@param children: 子要素（文字列またはXmlElement型の可変引数）
		@return: タグ要素
		"""
		return XmlElement(tag, attr, children, None)

	
	@staticmethod
	def createText(text = ""):
		""" テキスト要素を作成

		@param text: テキスト文字列
		@return: テキスト要素
		"""
		return XmlElement(None, {}, (), text)


	################################################################################
	# public
	
	def setAttribute(self, name, value):
		""" 属性を設定

		@param name: 属性名
		@param value: 属性値
		@return: 要素
		"""
		self.__attr[name] = value
		return self


	def setAttributes(self, attr):
		""" 複数の属性を一括設定

		@param attr: name:valueの辞書
		@return: 要素
		"""
		assert isinstance(attr, dict)
		self.__attr.update(attr)
		return self


	def removeAttributes(self, *names):
		""" 属性を削除

		@param names: 削除する属性名（可変引数）
		@return: 要素
		"""
		for name in names:
			if name in self.__attr:
				del self.__attr[name]
		return self


	def addChildren(self, *children):
		""" 子要素を追加

		@param children: 子要素（文字列またはXmlElement型の可変引数）
		@return: 要素
		"""
		return self.__addChildren(children)


	def emptyChildren(self):
		""" 子要素を全て削除

		@return: 要素
		"""
		self.__attr.clear()
		return self


	def toString(self):
		""" 要素を文字列化

		@return: 文字列化した要素
		"""
		# テキスト要素
		if self.__text != None:
			return self.__toString_Text()

		# タグ要素
		if self.__tag != None:
			return self.__toString_Tag()
	
		# ここには来ないはず
		return None


	################################################################################
	# private

	def __init__(self, tag, attr, children, text):
		""" コンストラクタ

		@param tag: タグ文字列
		@param attr: 属性情報（name:valueの辞書）
		@param children: 子要素（文字列またはXmlElement型の可変引数）
		@param text: テキスト文字列
		"""
		assert isinstance(attr, dict)
		assert isinstance(children, tuple)

		self.__text = text
		self.__tag  = tag
		self.__attr = attr

		# 子要素
		self.__children = None
		if children != ():
			self.__children = []
			self.__addChildren(children)

	
	def __addChildren(self, children):
		""" 子要素を追加（本体）

		@param children: 子要素（文字列またはXmlElement型の可変引数）
		@return: 要素
		"""
		for child in children:
			# 文字列型なら要素型に変換
			if type(child) is str:
				child = XmlElement.createText(child)

			assert isinstance(child, XmlElement)
			self.__children.append(child)
		return self


	def __toString_Text(self):
		""" 要素を文字列化: テキスト

		@return: 文字列化した要素
		"""
		return escape(self.__text)


	def __toString_Tag(self):
		""" 要素を文字列化: タグ

		@return: 文字列化した要素
		"""
		result = "<"

		# 開始
		tag = escape(self.__tag)
		result += tag

		# 属性
		for name, value in self.__attr.items():
			result += " %s=%s" % (escape(name), escape(value, quote = True))

		if self.__children == None:
			# 子要素なし
			result += " />"
		else:
			# 子要素あり
			result += ">"

			# 子要素
			for child in self.__children:
				result += child.toString()

			# タグを閉じる
			result += "</%s>" % (tag)

		return result


def test():
	""" 単体テスト """
	print("xmlutils test")

	# escape
	assert escape('''some meta characters will be <escaped>, but "single quotation" won't be escaped.''') == '''some meta characters will be &lt;escaped&gt;, but &quot;single quotation&quot; won't be escaped.'''
	assert escape('''these 'single quotations' will be escaped, and entire string will be quoted.''', apos = True, quote = True) == '''"these &apos;single quotations&apos; will be escaped, and entire string will be quoted."'''

	# XmlElement
	obj_xml_text = XmlElement.createText('''<span>this "span" tag will be escaped</span>''')
	obj_xml_br   = XmlElement.create("br").setAttribute("name", "value")
	obj_xml = XmlElement.create("div", {"id": "wrapper"}, "text", obj_xml_br).addChildren(obj_xml_text, obj_xml_br)
	assert obj_xml.toString() == '''<div id="wrapper">text<br name="value" />&lt;span&gt;this &quot;span&quot; tag will be escaped&lt;/span&gt;<br name="value" /></div>'''
	
	print("OK")


# test
if __name__ == "__main__":
	test()
