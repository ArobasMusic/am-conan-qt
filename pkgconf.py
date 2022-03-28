import os

version = "5.15.3"
packageVersion = "{}-{}".format(version, os.getenv('BUILD_NUMBER', '0'))
