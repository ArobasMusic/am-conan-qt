import os

version = "5.9.7-{}".format(os.getenv('BUILD_NUMBER', '0'))
branch = "v5.9.7"
