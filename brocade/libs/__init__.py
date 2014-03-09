# -*- coding: utf-8 -*-
""" 外部ライブラリ

ライブラリ本体は "__archives"以下に展開し、このディレクトリにはシンボリックリンクを配置
"""

# このディレクトリを検索パスの先頭に追加
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
