import os
from distutils.spawn import find_executable
from conans import ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count


class QtConan(ConanFile):
    name = "Qt"
    version = "5.9.3"
    description = "Conan.io package for Qt library."
    source_dir = "qt5"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "opengl": ["desktop", "dynamic"],
        "openssl": ["no", "yes", "linked"],
        "canvas3d": [True, False],
        "gamepad": [True, False],
        "graphicaleffects": [True, False],
        "location": [True, False],
        "serialport": [True, False],
        "tools": [True, False],
        "webengine": [True, False],
        "websockets": [True, False]
    }
    default_options = "canvas3d=False", "gamepad=False", "graphicaleffects=False", "location=False", "opengl=dynamic", "openssl=no", "serialport=False", "tools=False", "webengine=False", "websockets=False"
    url = "https://github.com/ArobasMusic/conan-qt"
    license = "http://doc.qt.io/qt-5/lgpl.html"
    short_paths = True

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.opengl
            del self.options.openssl

    def requirements(self):
        if self.settings.os == "Windows":
            if self.options.openssl == "yes":
                self.requires("OpenSSL/1.0.2l@conan/stable", dev=True)
            elif self.options.openssl == "linked":
                self.requires("OpenSSL/1.0.2l@conan/stable")

    def source(self):
        submodules = ["qtbase", "qtconnectivity", "qtimageformats", "qtmultimedia", "qtsvg", "qttools", "qtxmlpatterns"]
        if self.settings.os == "Windows":
            submodules.append("qtwinextras")
        else:
            submodules.append("qtmacextras")
        for module in ["canvas3d", "gamepad", "graphicaleffects", "location", "serialport", "tools", "webengine", "websockets"]:
            option = self.options[module]
            if option.value:
                submodules.append("qt{}".format(module))
        self.run("git clone https://code.qt.io/qt/qt5.git")
        self.run("cd {} && git checkout v{}".format(self.source_dir, self.version))
        self.run("cd {} && perl init-repository --no-update --module-subset={}".format(self.source_dir, ",".join(submodules)))
        self.run("cd {} && git submodule update".format(self.source_dir))
        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.source_dir))

    def build(self):
        args = [
            "-opensource",
            "-confirm-license",
            "-nomake examples",
            "-nomake tests",
            "-prefix {}".format(self.package_folder)
        ]
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                args.append("-debug")
            else:
                args.append("-debug-and-release")
        else:
            args.append("-release")
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_msvc(args)
        else:
            self._build_unix(args)

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
        args += ["-opengl {}".format(self.options.opengl)]
        if self.options.opengl == "dynamic":
            args += ["-angle"]
            env.update({'QT_ANGLE_PLATFORM': 'd3d11'})
        if self.options.openssl == "no":
            args += ["-no-openssl"]
        elif self.options.openssl == "yes":
            args += ["-openssl"]
        else:
            args += ["-openssl-linked"]
        env_build = VisualStudioBuildEnvironment(self)
        env.update(env_build.vars)
        with tools.environment_append(env):
            vcvars = tools.vcvars_command(self.settings)
            self.run("cd {} && {} && set".format(self.source_dir, vcvars))
            self.run("cd {} && {} && configure {}".format(self.source_dir, vcvars, " ".join(args)))
            self.run("cd {} && {} && {} {}".format(self.source_dir, vcvars, build_command, " ".join(build_args)))
            self.run("cd {} && {} && {} install".format(self.source_dir, vcvars, build_command))

    def _build_unix(self, args):
        args += ["-silent"]
        if self.settings.arch == "x86":
            args += ["-platform macx-clang-32"]
        self.output.info("Using '{}' threads".format(cpu_count()))
        self.run("cd {} && ./configure {}".format(self.source_dir, " ".join(args)))
        self.run("cd {} && make -j {}".format(self.source_dir, cpu_count()))
        self.run("cd {} && make install".format(self.source_dir))

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*", dst="src", src=os.path.join(self.source_folder, self.source_dir))

    def package_info(self):
        libs = [
            'Concurrent',
            'Core',
            'DBus',
            'Gui',
            'Network',
            'OpenGL',
            'Sql',
            'Test',
            'Widgets',
            'Xml'
        ]
        self.cpp_info.libs = []
        self.cpp_info.includedirs = ["include"]
        for lib in libs:
            if self.settings.os == "Windows" and self.settings.build_type == "Debug":
                suffix = "d"
            elif self.settings.os == "Macos" and self.settings.build_type == "Debug":
                suffix = "_debug"
            else:
                suffix = ""
            self.cpp_info.libs += ["Qt5{}{}".format(lib, suffix)]
            self.cpp_info.includedirs += ["include/Qt{}".format(lib)]
        if self.settings.os == "Windows":
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
