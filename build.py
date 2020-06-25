from conan.packager import ConanMultiPackager
from conans.client.loader import parse_conanfile
from conans.client.graph.python_requires import ConanPythonRequire


def build():
    (_, conanfile) = parse_conanfile('./conanfile.py', ConanPythonRequire(None, None))
    builder = ConanMultiPackager(
        reference="{}/{}".format(conanfile.name, conanfile.version),
        username="arobasmusic",
    )
    builder.add_common_builds()
    builder.remove_build_if(lambda build: build.settings["build_type"] == "Debug")
    builder.run()

if __name__ == "__main__":
    build()
