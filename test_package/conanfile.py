""" PyLint is boring """

import os
from conans import ConanFile, CMake

# This easily allows to copy the package in other user or channel
CHANNEL = os.getenv("CONAN_CHANNEL", "stable")
USERNAME = os.getenv("CONAN_USERNAME", "amusic")


class QtTestConan(ConanFile):
    """ Qt Conan package test """

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "virtualenv"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self.settings.os == "Windows":
            self.run("activate && ctest -C Release")
        else:
            self.run("ctest")
