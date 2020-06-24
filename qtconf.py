import os

QT_VERSION = "5.15"

BRANCH = "{}".format(QT_VERSION)
PKG_VERSION = "{}-{}".format(QT_VERSION, os.getenv('BUILD_NUMBER', '0'))
