import os

version = "5.12.5-{}".format(os.getenv('BUILD_NUMBER', '0'))
branch = "v5.12.5"
