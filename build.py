import os
import platform
import re

from conans.client.conan_api import Conan
from conans.client.loader import ConanFileLoader
from conans.client.graph.python_requires import ConanPythonRequire


def default(col, index, fallback):
    try:
        return col[index]
    except IndexError:
        return fallback

def get_remote(conan_api):
    remote = os.getenv('CONAN_UPLOAD', 'http://conan.arobas-music.com@True@arobasmusic').split('@')

    remote_url = remote[0]
    remote_verify_ssl = default(remote, 1, 'True').lower() in ['true', 'yes']
    remote_name = default(remote, 2, 'arobasmusic')

    user = os.getenv("CONAN_LOGIN_USERNAME_{}".format(remote_name.upper()), os.getenv("CONAN_LOGIN_USERNAME"))
    password = os.getenv("CONAN_PASSWORD_{}".format(remote_name.upper()), os.getenv("CONAN_PASSWORD"))

    for registered_remote in conan_api.remote_list():
        if registered_remote.name == remote_name and registered_remote.url == remote_url:
            return (remote_name,user,password)

    conan_api.remote_add(remote_name, remote_url, remote_verify_ssl)
    return (remote_name,user,password)

def get_archs():
    return map(lambda s: s.strip(), os.getenv('CONAN_ARCHS', 'x86,x86_64').split(','))

def get_compiler():
    platform_os = platform.system()
    if platform_os == "Windows":
        return "Visual Studio"
    elif platform_os == "Darwin":
        return "apple-clang"
    raise Exception("Error unsupported platform: {}".format(platform_os))

def get_compiler_versions():
    platform_os = platform.system()
    if platform_os == "Windows":
        return map(lambda s: s.strip(), os.environ['CONAN_VISUAL_VERSIONS'].split(','))
    elif platform_os == "Darwin":
        return map(lambda s: s.strip(), os.environ['CONAN_APPLE_CLANG_VERSIONS'].split(','))
    raise Exception("Error unsupported platform: {}".format(platform_os))

def get_channel():
    branch = os.environ['BRANCH_NAME']
    if re.match(os.getenv("CONAN_STABLE_BRANCH_PATTERN", "^master$"), branch):
        return "stable"
    return "testing"

# Create package
def build(conan_api):
    compiler = get_compiler()
    channel = get_channel()
    for arch in get_archs():
        for compiler_version in get_compiler_versions():
            conan_api.create(
                "./conanfile.py",
                user="arobasmusic",
                channel=channel,
                settings=[
                    "arch={}".format(arch),
                    "compiler={}".format(compiler),
                    "compiler.version={}".format(compiler_version),
                ]
            )

# Upload package
def upload(conan_api):
    remote, user, password = get_remote(conan_api)
    conan_api.authenticate(user, password, remote)

    channel = get_channel()
    conanfile = ConanFileLoader(None, None, ConanPythonRequire(None, None)).load_class('./conanfile.py')
    conan_api.upload(
        pattern="{}/{}@arobasmusic/{}".format(conanfile.name, conanfile.version, channel),
        remote_name=remote
    )

if __name__ == "__main__":
    (conan_api, _, _) = Conan.factory()
    build(conan_api)
    upload(conan_api)
