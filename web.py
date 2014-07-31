#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
""" ウェブアプリケーションインターフェース

@author: shimataro
"""

import root
from private.application import create_application
application = create_application(root.get_root_dir())


if __name__ == "__main__":
	# テストサーバ起動
	application.test_run()
