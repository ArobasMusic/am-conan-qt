import os

VERSION = "6.0.0"
PACKAGE_VERSION = f"{VERSION}-{os.getenv('BUILD_NUMBER', '0')}"
