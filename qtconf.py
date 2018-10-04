import os
version = "5.9.7-{}".format(os.getenv('BUILD_NUMBER', '0'))
branch = "5.9.7" # utlisé pour git checkout
