import os
import shutil

from distutils.spawn import find_executable
from conans import ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count

import qtconf

class QtConan(ConanFile):
    name = "Qt"
    version = qtconf.PKG_VERSION
    description = "Conan.io package for Qt library."
    source_dir = "qt5"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "opengl": ["no", "desktop", "dynamic"],
        "openssl": ["no", "yes", "linked"],
        "universal_binary": [True, False],
    }
    no_copy_source = True
    exports = ["LICENSE.md", "qtconf.py"]
    exports_sources = ["patches/*"]
    default_options = (
        "opengl=no",
        "openssl=yes",
        "universal_binary=False",
    )
    url = "https://github.com/ArobasMusic/conan-qt"
    license = "http://doc.qt.io/qt-5/lgpl.html"
    short_paths = True


    @property
    def openssl_prefix_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath

    def build_arches(self):
        if self.settings.os == "Macos" and self.options.universal_binary:
            yield "arm64"
            yield "x86_64"
        elif self.settings.arch == "armv8":
            yield "arm64"
        elif self.settings.arch == "x86_64":
            yield "x86_64"

    def configure(self):
        if self.settings.arch == "x86":
            raise Exception("Unsupported architecture 'x86'")

        if self.settings.os != "Linux":
            del self.settings.build_type

        if self.settings.os == "Macos":
            del self.settings.os.version
            if self.options.universal_binary:
                del self.settings.arch

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
        if self.settings.os == "Windows":
            self.build_requires("strawberryperl/5.30.0.1")
            if self.options.openssl == "yes":
                self.build_requires("OpenSSL/1.1.1m-2@arobasmusic/stable")

    def requirements(self):
        if self.settings.os == "Windows":
            if self.options.openssl == "linked":
                self.requires("OpenSSL/1.1.1m-2@arobasmusic/stable")

    def source(self):
        submodules = ["qtbase", "qtimageformats", "qtsvg", "qttools", "qttranslations", "qtxmlpatterns"]

        if self.settings.os == "Macos":
            submodules.append("qtmacextras")

        if self.settings.os == "Windows":
            submodules.append("qtwinextras")

        git = tools.Git(self.source_dir)
        git.clone(**self.conan_data["sources"][qtconf.QT_VERSION])

        self.run("cd {} && perl init-repository --no-update --module-subset={}".format(self.source_dir, ",".join(submodules)))
        self.run("cd {} && git submodule update".format(self.source_dir))

        for patch in self.conan_data["patches"].get(qtconf.QT_VERSION, []):
            self.output.info("Applying patch {}".format(patch["patch_file"]))
            tools.patch(**patch)

        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.source_dir))

    def build(self):
        args = [
            "-opensource",
            "-confirm-license",
            "-nomake examples",
            "-nomake tests",
            "-no-sql-mysql",
        ]
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_msvc(args)
        elif self.settings.os == "Linux" and self.settings.compiler == "clang":
            self._build_linux_clang(args)
        elif self.settings.os == "Macos":
            if self.options.universal_binary:
                self._build_macos_univerval_binary(args)
            else:
                self._build_macos(args)
        else:
            raise Exception("Unsupport configuration os='{}' compiler={}".format(
                self.settings.os,
                self.settings.compiler
            ))

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

        if self.options.openssl == "linked":
            args += ["-openssl-linked"]
        elif self.options.openssl == "yes":
            args += ["-openssl", f"OPENSSL_PREFIX={self.openssl_prefix_dir}"]
        else:
            args += ["-no-openssl"]

        args += [
            "-direct2d",
            "-debug-and-release",
            "-force-debug-info",
            "-separate-debug-info",
            f"-prefix {self.package_folder}",
        ]

        build_env = tools.vcvars_dict(self)
        configure_script = os.path.join(self.source_folder, "qt5", "configure.bat")
        with tools.environment_append(build_env):
            self.run(f"{configure_script} {' '.join(args)}", cwd=self.build_folder)
            self.run(f"{build_command} {' '.join(build_args)}", cwd=self.build_folder)
            self.run(f"{build_command} install", cwd=self.build_folder)

    def _build_macos(self, args):
        configure = os.path.join(self.source_folder, "qt5", "configure")
        os_version = self.settings.get_safe('os.version', default="10.13")
        arch = "arm64" if self.settings.arch == "armv8" else "x86_64"
        args += [
            "-debug-and-release",
            "-force-debug-info",
            "-no-framework",
            "-platform macx-clang",
            f"-prefix {self.package_folder}",
            "-silent",
            "-separate-debug-info",
            f"QMAKE_MACOSX_DEPLOYMENT_TARGET='{os_version}'",
            f"QMAKE_APPLE_DEVICE_ARCHS='{arch}'"
        ]
        self.run(f"{configure} {' '.join(args)} ", cwd=self.build_folder)
        self.run(f"make -j {cpu_count()}", cwd=self.build_folder)
        self.run("make install", cwd=self.build_folder)

    def _build_macos_univerval_binary(self, args):
        configure = os.path.join(self.source_folder, "qt5", "configure")
        os_version = self.settings.get_safe("os.version", default="10.13")
        args += [
            "-no-framework",
            "-platform macx-clang",
            "-release",
            "-silent",
            f"QMAKE_MACOSX_DEPLOYMENT_TARGET={os_version}",
        ]
        # build Qt for all arch
        for arch in self.build_arches():
            tools.mkdir(arch)
            arch_build_dir = os.path.join(self.build_folder, arch)
            arch_prefix_dir = os.path.join(arch_build_dir, "INSTALL")
            self.run(
                f"{configure} -prefix '{arch_prefix_dir}' {' '.join(args)} QMAKE_APPLE_DEVICE_ARCHS={arch}",
                cwd=arch_build_dir
            )
            self.run(f"make -j {cpu_count()}", cwd=arch_build_dir)
            self.run("make install", cwd=arch_build_dir)

    def _build_linux_clang(self, args):
        args += [
            "-silent",
            "-platform linux-clang"
        ]

        if self.options.get_safe("opengl") == "no":
            args += ["-no-opengl"]

        configure_script = os.path.join(self.source_folder, "qt5", "configure.bat")

        self.run(f"{configure_script} {' '.join(args)}", cwd=self.build_folder)
        self.run("make -j {}".format(cpu_count()), cwd=self.build_folder)
        self.run("make install", cwd=self.build_folder)


    def package_id(self):
        if self.settings.os == "Macos" and self.options.universal_binary:
            del self.info.settings.arch

    def package(self):
        if self.settings.os == "Macos" and self.options.universal_binary:
            self._package_macos_universal_binary()
        else:
            source_path = os.path.join(self.source_folder, self.source_dir)
            self.copy("*", dst="src", src=source_path)

    def _package_macos_universal_binary(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        lib_folder = os.path.join(self.package_folder, "lib")
        plugins_folder = os.path.join(self.package_folder, "plugins")

        tools.mkdir(bin_folder)
        tools.mkdir(lib_folder)
        tools.mkdir(plugins_folder)

        for dir in (
            "include",
            "mkspecs",
            "phrasebooks",
            "translations",
            os.path.join("lib", "cmake"),
            os.path.join("lib", "pkgconfig"),
            os.path.join("lib", "metatypes"),
        ):
            self.copy("*", dst=dir, src=os.path.join(self.build_folder, "arm64", "INSTALL", dir))

        for file in (
            "lconvert",
            "lprodump",
            "lrelease",
            "lrelease-pro",
            "lupdate",
            "lupdate-pro",
            "macchangeqt",
            "macdeployqt",
            "moc",
            "qcollectiongenerator",
            "qdbus",
            "qdbuscpp2xml",
            "qdbusxml2cpp",
            "qhelpgenerator",
            "qlalr",
            "qtattributionsscanner",
            "qtdiag",
            "qtpaths",
            "qtplugininfo",
            "qvkgen",
            "rcc",
            "tracegen",
            "uic",
            "xmlpatterns",
            "xmlpatternsvalidator",
        ):
            inputs = [os.path.join(self.build_folder, arch, "INSTALL", "bin", file) for arch in self.build_arches()]
            self.run(
                f"lipo -create -output {file} {' '.join(inputs)}",
                cwd=bin_folder
            )

        shutil.copyfile(
            os.path.join(self.build_folder, "x86_64", "INSTALL", "bin", "qmake"),
            os.path.join(self.package_folder, "bin", "qmake"),
        )

        for lib in (
            "libQt5DesignerComponents",
            "libQt5Designer",
            "libQt5Help",
            "libQt5Widgets",
            "libQt5OpenGL",
            "libQt5Core",
            "libQt5Svg",
            "libQt5Network",
            "libQt5PrintSupport",
            "libQt5MacExtras",
            "libQt5Concurrent",
            "libQt5Test",
            "libQt5Sql",
            "libQt5DBus",
            "libQt5XmlPatterns",
            "libQt5Xml",
            "libQt5Gui"
        ):
            file = f"{lib}.{qtconf.QT_VERSION}.dylib"
            inputs = [os.path.join(self.build_folder, arch, "INSTALL", "lib", file) for arch in self.build_arches()]
            self.run(
                f"lipo -create -output {file} {' '.join(inputs)}",
                cwd=lib_folder
            )

            dylib_version = qtconf.QT_VERSION.split(".")
            self.run(
                f"ln -s {file} {lib}.{'.'.join(dylib_version[0:2])}.dylib",
                cwd=lib_folder
            )
            self.run(
                f"ln -s {file} {lib}.{'.'.join(dylib_version[0:1])}.dylib",
                cwd=lib_folder
            )

        for plugin in (
            os.path.join("bearer", "libqgenericbearer.dylib",),
            os.path.join("generic", "libqtuiotouchplugin.dylib",),
            os.path.join("iconengines", "libqsvgicon.dylib",),
            os.path.join("imageformats", "libqgif.dylib",),
            os.path.join("imageformats", "libqicns.dylib",),
            os.path.join("imageformats", "libqico.dylib",),
            os.path.join("imageformats", "libqjpeg.dylib",),
            os.path.join("imageformats", "libqmacheif.dylib",),
            os.path.join("imageformats", "libqmacjp2.dylib",),
            os.path.join("imageformats", "libqsvg.dylib",),
            os.path.join("imageformats", "libqtga.dylib",),
            os.path.join("imageformats", "libqtiff.dylib",),
            os.path.join("imageformats", "libqwbmp.dylib",),
            os.path.join("imageformats", "libqwebp.dylib",),
            os.path.join("platforms", "libqcocoa.dylib",),
            os.path.join("platforms", "libqminimal.dylib",),
            os.path.join("platforms", "libqoffscreen.dylib",),
            os.path.join("platformthemes", "libqxdgdesktopportal.dylib",),
            os.path.join("printsupport", "libcocoaprintersupport.dylib",),
            os.path.join("sqldrivers", "libqsqlite.dylib",),
            os.path.join("styles", "libqmacstyle.dylib",),
        ):
            tools.mkdir(os.path.join(plugins_folder, os.path.dirname(plugin)))
            inputs = [os.path.join(self.build_folder, arch, "INSTALL", "plugins", plugin) for arch in self.build_arches()]
            self.run(
                f"lipo -create -output {plugin} {' '.join(inputs)}",
                cwd=plugins_folder,
            )
