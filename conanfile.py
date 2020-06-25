import os

from distutils.spawn import find_executable
from conans import ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count

import qtconf

class QtConan(ConanFile):
    name = "Qt"
    version = qtconf.PKG_VERSION
    description = "Conan.io package for Qt library."
    source_dir = "qt5"
    settings = "os", "arch", "compiler"
    options = {
        "canvas3d": [True, False],
        "framework": [True, False],
        "connectivity": [True, False],
        "gamepad": [True, False],
        "graphicaleffects": [True, False],
        "location": [True, False],
        "opengl": ["no", "desktop", "dynamic"],
        "openssl": ["no", "yes", "linked"],
        "serialport": [True, False],
        "tools": [True, False],
        "webengine": [True, False],
        "websockets": [True, False],
    }
    exports = ["LICENSE.md", "qtconf.py"]
    default_options = "canvas3d=False", "connectivity=False", "framework=False", "gamepad=False", "graphicaleffects=False", "location=False", "opengl=no", "openssl=yes", "serialport=False", "tools=False", "webengine=False", "websockets=False"
    url = "https://github.com/ArobasMusic/conan-qt"
    license = "http://doc.qt.io/qt-5/lgpl.html"
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
                self.options["openssl"].no_zlib = True
                self.options["openssl"].shared = True

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.opengl
            del self.options.openssl
        else:
            del self.options.framework

    def build_requirements(self):
        if self.settings.os == "Windows":
            if self.options.openssl == "yes":
                self.build_requires("openssl/1.1.1g")

    def requirements(self):
        if self.settings.os == "Windows":
            if self.options.openssl == "linked":
                self.requires("openssl/1.1.1g")

    def source(self):
        submodules = ["qtbase", "qtimageformats", "qtmultimedia", "qtsvg", "qttools", "qttranslations", "qtxmlpatterns"]
        if self.settings.os == "Windows":
            submodules.append("qtwinextras")
        else:
            submodules.append("qtmacextras")
        for module in ["connectivity", "canvas3d", "gamepad", "graphicaleffects", "location", "serialport", "tools", "webengine", "websockets"]:
            option = self.options[module]
            if option.value:
                submodules.append("qt{}".format(module))
        self.run("git clone https://code.qt.io/qt/qt5.git")
        self.run("cd {} && git checkout {}".format(self.source_dir, qtconf.BRANCH))
        self.run("cd {} && perl init-repository --no-update --module-subset={}".format(self.source_dir, ",".join(submodules)))
        self.run("cd {} && git submodule update".format(self.source_dir))
        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.source_dir))

    def build(self):
        args = [
            "-debug-and-release",
            "-opensource",
            "-confirm-license",
            "-nomake examples",
            "-nomake tests",
            "-no-sql-mysql",
            "-force-debug-info",
            "-separate-debug-info",
            "-prefix {}".format(self.package_folder)
        ]
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_msvc(args)
        else:
            self._build_macos(args)

    def _build_msvc(self, args):
        build_command = find_executable("jom.exe")
        if build_command:
            build_args = ["-j", str(cpu_count())]
        else:
            build_command = "nmake.exe"
            build_args = []
        self.output.info("Using '{} {}' to build".format(build_command, " ".join(build_args)))
        env = {}
        env.update({'PATH': [
            "C:\\Perl64\\bin",
            "C:\\Program Files (x86)\\Windows Kits\\8.1\\bin\\x86",
            "{}\\qtbase\\bin".format(self.build_folder),
            "{}\\gnuwin32\\bin".format(self.build_folder),
            "{}\\qtrepotools\\bin".format(self.build_folder)
        ]})
        # it seems not enough to set the vcvars for older versions
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == "14":
                args += ["-platform win32-msvc2015"]

        if self.options.opengl == "no":
            args += ["-no-opengl"]
        else:
            args += ["-opengl {}".format(self.options.opengl)]
            if self.options.opengl == "dynamic":
                args += ["-angle"]
                env.update({'QT_ANGLE_PLATFORM': 'd3d11'})

        if self.options.openssl == "no":
            args += ["-no-openssl"]
        elif self.options.openssl == "yes":
            args += ["-openssl", "OPENSSL_PREFIX={}".format(self.openssl_prefix_dir)]
        else:
            args += ["-openssl-linked"]

        args += ["-direct2d"]
        env_build = VisualStudioBuildEnvironment(self)
        env.update(env_build.vars)
        with tools.environment_append(env):
            vcvars = tools.vcvars_command(self.settings)
            self.run("{} && configure {}".format(vcvars, " ".join(args)), cwd=self.build_dir)
            self.run("{} && {} {}".format(vcvars, build_command, " ".join(build_args)), cwd=self.build_dir)
            self.run("{} && {} install".format(vcvars, build_command), cwd=self.build_dir)

    def _build_macos(self, args):
        os_version = self.settings.get_safe('os.version')

        args += ["-silent"]
        args += ["-framework" if self.options.framework else "-no-framework"]
        args += ["-platform macx-clang"]
        args += ["QMAKE_MACOSX_DEPLOYMENT_TARGET={}".format(os_version if os_version else "10.13")]
        self.output.info("Using '{}' threads".format(cpu_count()))
        self.run("./configure {}".format(" ".join(args)), cwd=self.build_dir)
        self.run("make -j {}".format(cpu_count()), cwd=self.build_dir)
        self.run("make install", cwd=self.build_dir)

    def package(self):
        self.copy("*", dst="src", src=os.path.join(self.source_folder, self.source_dir))
