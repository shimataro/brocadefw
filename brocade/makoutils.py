# -*- coding: utf-8 -*-
""" Mako用ユーティリティ """

from .libs import mako
from mako.lookup import TemplateLookup
from mako.cache import register_plugin

register_plugin("dictcache", __name__, "DictCache")


def get_lookup(base_dir = "templates", languages = None, default_language = "ja", template_type = "html", device = "default", lookup_params = {}):
	""" テンプレート検索オブジェクトを取得

	@param base_dir: テンプレートファイルがあるベースディレクトリ
	@param languages: 使用する言語の順位
	@param default_language: どれも使えない場合に使うデフォルト言語
	@param template_type: テンプレートの種類
	@param device: デバイスの種類
	@param lookup_params: TemplateLookupに渡すパラメータ
	@return: テンプレート検索オブジェクト
	"""
	lookup_params_ = lookup_params.copy()
	lookup_params_.update({
		"directories"    : __get_lookup_directories(base_dir, languages, default_language, template_type, device),
		"input_encoding" : "utf-8",
		"output_encoding": "utf-8",
		"encoding_errors": "replace",
		"cache_impl": "dictcache",
	})
	return TemplateLookup(**lookup_params_)


def __get_lookup_directories(base_dir, languages, default_language, template_type, device):
	""" テンプレートの検索場所一覧を取得

	@param base_dir: テンプレートファイルがあるベースディレクトリ
	@param languages: 使用する言語の順位
	@param default_language: どれも使えない場合に使うデフォルト言語
	@param template_type: テンプレートの種類
	@param device: デバイスの種類
	@return: 検索場所一覧
	"""

	# 言語一覧
	if languages == None:
		languages = []
	languages.append(default_language)

	# デバイス一覧
	devices = [device]
	if device != "default":
		devices.append("default")

	# ディレクトリ一覧
	directories = []
	for language in languages:
		directory = "%s/%s/%s" % (base_dir, language, template_type)

		if template_type == "html":
			# HTMLならデバイス別ディレクトリを設定
			for device in devices:
				directories.append("%s/%s" % (directory, device))

		else:
			directories.append(directory)

	return directories


class DictCache(object):
	""" 辞書によるインメモリの揮発性キャッシュ """
	pass_context = False

	__cache = {}

	def __init__(self, cache):
		self.cache = cache


	def get_or_create(self, key, creation_function, **kwargs):
		if key in self.__cache:
			return self.__cache[key]

		else:
			self.__cache[key] = value = creation_function()

		return value


	def set(self, key, value, **kwargs):
		self.__cache[key] = value


	def get(self, key, **kwargs):
		return self.__cache.get(key)


	def invalidate(self, key, **kwargs):
		self.__cache.pop(key, None)
