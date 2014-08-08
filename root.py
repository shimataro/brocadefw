# -*- coding: utf-8 -*-
""" ルートスクリプト

@author: shimataro
"""

from os.path import dirname, abspath
_root_dir = dirname(abspath(__file__))

def get_root_dir():
	""" ルートディレクトリを取得

	@return ルートディレクトリ
	"""
	return _root_dir
