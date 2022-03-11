import os

version = "5.15.2"
packageVersion = "{}-{}".format(version, os.getenv('BUILD_NUMBER', '0'))
