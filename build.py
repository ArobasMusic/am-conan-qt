from conans.client.loader_parse import load_conanfile_class as ConanFile
from conan.packager import ConanMultiPackager

def build():
    conanfile = ConanFile('./conanfile.py')
    builder = ConanMultiPackager(
        reference="{}/{}".format(conanfile.name, conanfile.version),
        username="amusic",
    )
    builder.add_common_builds()
    builder.run()

if __name__ == "__main__":
    build()
