# -*- coding: utf-8 -*-
""" 国際化モジュール

@author: shimataro
"""
from importlib import import_module

LANGUAGE_MODULE_NAME = "brocade.i18n.languages"
LOCALE_MODULE_NAME   = "brocade.i18n.locales"

class I18n:
	""" 国際化クラス """

	def __init__(self, message_module_name, accept_languages = [], default_language = "ja-JP"):
		""" コンストラクタ

		@param message_module_name: メッセージモジュールの場所
		@param accept_languages: 希望の言語一覧（IETF言語タグ"language"または"language-region"）
		@param default_language: 希望の言語を使えなかった場合のデフォルト言語（"language-region"）
		"""
		self.__message_module_name = message_module_name
		self.__accept_languages = accept_languages
		self.__default_language = default_language

		# モジュールをロード
		self.__module_message_keys = import_module(message_module_name)
		(self.__module_messages, self.__module_language, self.__module_locale) = self.__find_modules()


	def get_message(self, key, params = {}):
		""" メッセージ取得

		@param key: メッセージキー
		@param params: メッセージを置き換えるパラメータ
		@return: メッセージ
		"""
		return self.__module_messages.messages[key].format(**params)


	def get_message_keys(self):
		""" メッセージキーオブジェクトを取得

		@return: メッセージキーオブジェクト
		"""
		return self.__module_message_keys


	def get_language_info(self):
		""" 言語オブジェクトを取得

		@return: 言語オブジェクト
		"""
		return self.__module_language


	def get_locale_info(self):
		""" ロケールオブジェクトを取得

		@return: ロケールオブジェクト
		"""
		return self.__module_locale


	def __find_modules(self):
		""" 最適なモジュールを検索

		@return: ([メッセージモジュール], [言語モジュール], [ロケールモジュール])
		"""
		for language in self.__accept_languages:
			try:
				return self.__load_modules(language)

			except ImportError:
				pass

		return self.__load_modules(self.__default_language)


	def __load_modules(self, language):
		""" 指定のモジュールをロード

		@param language: 言語情報（"en-US", "ja"等）
		@return: ([メッセージモジュール], [言語モジュール], [ロケールモジュール])
		"""
		language_detail = language.split("-", 2)
		language = language_detail[0].lower()

		# メッセージモジュールをロード
		module_messages = import_module("%s.%s" % (self.__message_module_name, language))

		# 言語モジュールをロード
		module_language = import_module("%s.%s" % (LANGUAGE_MODULE_NAME, language))

		# ロケールモジュール名を決定
		locale = module_language.DEFAULT_LOCALE
		if len(language_detail) > 1:
			locale = language_detail[1]

		# ロケールモジュールをロード
		locale = locale.lower()
		module_locale = import_module("%s.%s" % (LOCALE_MODULE_NAME, locale))
		return (module_messages, module_language, module_locale)


	message_keys  = property(get_message_keys)
	language_info = property(get_language_info)
	locale_info   = property(get_locale_info)
