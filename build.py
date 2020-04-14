import os
import platform

from fnmatch import fnmatch

from conans.client.conan_api import Conan
from conans.client.graph.python_requires import ConanPythonRequire
from conans.client.loader import parse_conanfile

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
            return (remote_name, user, password)

    conan_api.remote_add(remote_name, remote_url, remote_verify_ssl)
    return (remote_name, user, password)

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
    stable_branch_pattern = os.getenv("CONAN_STABLE_BRANCH_PATTERN", "release/*")
    if fnmatch(branch, stable_branch_pattern):
        return "stable"
    return "testing"

# Create package
def build(conan_api):
    compiler = get_compiler()
    channel = get_channel()
    options = [ "Qt:openssl=yes"] if platform.system() == "Windows" else []
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
                ],
                options=options
            )

# Upload package
def upload(conan_api):
    remote, user, password = get_remote(conan_api)
    conan_api.authenticate(user, password, remote)

    (_, conanfile) = parse_conanfile('./conanfile.py', ConanPythonRequire(None, None))
    conan_api.upload(
        pattern="{}/{}@arobasmusic/{}".format(conanfile.name, conanfile.version, get_channel()),
        remote_name=remote
    )

if __name__ == "__main__":
    (CONAN_API, _, _) = Conan.factory()
    build(CONAN_API)
    upload(CONAN_API)
