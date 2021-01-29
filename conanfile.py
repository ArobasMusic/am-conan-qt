import os

from distutils.spawn import find_executable
from conans import CMake, ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count

import qtconf

class QtConan(ConanFile):
    name = "Qt"
    version = qtconf.PACKAGE_VERSION
    description = "Conan.io package for Qt library."
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "framework": [True, False],
    }
    default_options = "framework=False",
    exports = "LICENSE.md", "qtconf.py",
    license = "http://doc.qt.io/qt-5/lgpl.html"
    url = "https://github.com/ArobasMusic/conan-qt"
    no_copy_source = True
    short_paths = True

    @property
    def build_dir(self):
        return os.path.join(self.build_folder, "qt5")

    @property
    def openssl_prefix_dir(self):
        return self.deps_cpp_info['openssl'].rootpath

    def configure(self):
        if self.settings.arch == "x86":
            raise Exception("Unsupported architecture 'x86'")
        if self.settings.os == "Windows":
            del self.settings.compiler.runtime
            if self.options.openssl in ["yes", "linked"]:
                self.options["openssl"].shared = True

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.openssl
        if self.settings.os == "Macos":
            del self.options.opengl
        if self.settings.os != "Macos":
            del self.options.framework

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")
        if self.settings.os == "Windows" and self.options.openssl == "yes":
            self.build_requires("openssl/1.1.1g")

    def requirements(self):
        if self.settings.os == "Windows" and self.options.openssl == "linked":
            self.requires("openssl/1.1.1g")

    def source(self):
        git = tools.Git(folder="qt")
        git.clone("https://code.qt.io/qt/qt5.git")
        git.checkout(f"v{qtconf.VERSION}")
        self.run("perl init-repository", cwd=os.path.join(self.source_folder, "qt"))

    def build(self):
        cmake_definitions = {
            "BUILD_SHARED_LIBS": "YES",
            "CMAKE_INSTALL_PREFIX": self.package_folder,
            "CMAKE_BUILD_TYPE": self.settings.build_type,
            "FEATURE_sql": "OFF",
            "FEATURE_dbus": "OFF",
            "QT_BUILD_TESTS": "OFF",
            "QT_BUILD_EXAMPLES": "OFF",
        }

        if self.settings.os == "Macos":
            cmake_definitions.update({
                "FEATURE_framework": "ON" if self.options.get_safe("framework") else "OFF",
                "QT_QMAKE_TARGET_MKSPEC": "macx-clang",
            })

        configure_args = " ".join([f"-D{var}={value}" for var, value in cmake_definitions.items()])

        self.run(f"{os.path.join(self.source_folder, 'qt', 'configure')} -- {configure_args}")
        cmake = CMake(self)
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            source_path = os.path.join(self.source_folder, "qt")
            self.copy("*", dst="src", src=source_path)
