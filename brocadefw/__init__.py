# -*- coding: utf-8 -*-
""" BrocadeFW """

import os, sys

def _get_dir():
	""" このファイルがあるディレクトリを取得 """
	return os.path.dirname(os.path.abspath(__file__))


# "libs"を検索パスに追加
sys.path.append(os.path.join(_get_dir(), "libs"))
