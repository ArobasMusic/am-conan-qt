import os
import platform

from conans.client.loader import ConanFileLoader
from conans.client.graph.python_requires import ConanPythonRequire

def run(command):
    retcode = os.system(command)
    if retcode != 0:
        raise Exception("Error while executing:\n\t %s" % command)

def get_archs():
    return map(lambda s: s.strip(), os.environ['CONAN_ARCHS'].split(','))

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

# Create package
def build():
    compiler = get_compiler()
    for arch in get_archs():
        for compiler_version in get_compiler_versions():
            run('''conan create . arobasmusic/stable -s arch={} -s compiler="{}" -s compiler.version={}'''.format(
                arch,
                compiler,
                compiler_version
            ))

# Upload package
def upload():
    loader = ConanFileLoader(None, None, ConanPythonRequire(None, None))
    conanfile = loader.load_class('./conanfile.py')
    user = os.environ['CONAN_LOGIN_USERNAME_AROBASMUSIC']
    password = os.environ['CONAN_PASSWORD_AROBASMUSIC']
    run("conan user --password {} --remote arobasmusic {}".format(
        password, user
    ))
    run("conan upload {}/{}@arobasmusic/stable --remote arobasmusic".format(
        conanfile.name, conanfile.version
    ))

if __name__ == "__main__":
    build()
    upload()
