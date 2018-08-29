from conan.packager import ConanMultiPackager

from conans.client.loader import ConanFileLoader
from conans.client.graph.python_requires import ConanPythonRequire

def build():
    loader = ConanFileLoader(None, None, ConanPythonRequire(None, None))
    conanfile = loader.load_class('./conanfile.py')
    builder = ConanMultiPackager(
        reference="{}/{}".format(conanfile.name, conanfile.version),
        username="amusic",
    )
    builder.add_common_builds()
    builder.run()

if __name__ == "__main__":
    build()
