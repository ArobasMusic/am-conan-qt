import os

version = "5.9.9-{}".format(os.getenv('BUILD_NUMBER', '0'))
branch = "5.9.9"
