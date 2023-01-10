import os
import shutil

from distutils.spawn import find_executable
from conans import ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count

import pkgconf

class QtConan(ConanFile):
    name = "Qt"
    version = pkgconf.packageVersion
    description = "Conan.io package for Qt library."
    source_dir = "qt5"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "opengl": ["no", "desktop", "dynamic"],
        "openssl": ["no", "yes", "linked"],
        "universal_binary": [True, False],
    }
    no_copy_source = True
    exports = ["LICENSE.md", "pkgconf.py"]
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
                self.build_requires("OpenSSL/1.1.1m-3@arobasmusic/stable")


    def requirements(self):
        if self.settings.os == "Windows":
            if self.options.openssl == "linked":
                self.requires("OpenSSL/1.1.1m-3@arobasmusic/stable")


    def source(self):
        submodules = [
            "qtbase",
            "qtimageformats",
            "qtsvg",
            "qttools",
            "qttranslations",
            "qtxmlpatterns",
            "qtmultimedia",
        ]

        if self.settings.os == "Macos":
            submodules.append("qtmacextras")

        if self.settings.os == "Windows":
            submodules.append("qtwinextras")

        git = tools.Git(self.source_dir)
        git.clone(**self.conan_data["sources"][pkgconf.version])

        self.run(
            f"perl init-repository --no-update --module-subset={','.join(submodules)}",
            cwd=self.source_dir,
        )
        self.run(
            f"git submodule update",
            cwd=self.source_dir,
        )

        for patch in self.conan_data["patches"].get(pkgconf.version, []):
            self.output.info("Applying patch {}".format(patch["patch_file"]))
            tools.patch(**patch)

        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.source_dir))


    def build(self):
        configure_args = [
            "-opensource",
            "-confirm-license",
            "-nomake examples",
            "-nomake tests",
            "-no-sql-mysql",
        ]
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_msvc(configure_args)
        elif self.settings.os == "Linux" and self.settings.compiler == "clang":
            self._build_linux_clang(configure_args)
        elif self.settings.os == "Macos":
            if self.options.universal_binary:
                self._build_macos_univerval_binary(configure_args)
            else:
                build_arch = "arm64" if self.settings.arch == "armv8" else "x86_64"
                configure_args += [
                    "-debug-and-release",
                    "-force-debug-info",
                    "-separate-debug-info",
                ]
                self._build_macos(
                    configure_args,
                    build_arch,
                    self.build_folder,
                    self.package_folder,
                )
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

    def _build_macos(self, configure_args, build_arch, build_folder, install_prefix):
        os_version = self.settings.get_safe('os.version', default="10.13")
        configure = os.path.join(self.source_folder, "qt5", "configure")
        configure_args += [
            "-no-framework",
            "-platform macx-clang",
            f"-prefix {install_prefix}",
            "-silent",
            f"QMAKE_MACOSX_DEPLOYMENT_TARGET='{os_version}'",
            f"QMAKE_APPLE_DEVICE_ARCHS='{build_arch}'"
        ]
        self.run(
            f"{configure} {' '.join(configure_args)} ",
            cwd=build_folder
        )
        self.run(
            f"make -j {cpu_count()}",
            cwd=build_folder
        )
        self.run(
            "make install",
            cwd=build_folder
        )

    def _build_macos_univerval_binary(self, configure_args):
        configure_args += ["-release"]
        # build Qt for all arch
        for build_arch in self.build_arches():
            build_folder = os.path.join(self.build_folder, build_arch)
            tools.mkdir(build_arch)
            self._build_macos(
                configure_args,
                build_arch,
                build_folder,
                install_prefix=os.path.join(build_folder, "INSTALL"),
            )

    def _build_linux_clang(self, args):
        args += [
            "-silent",
            "-platform linux-clang",
            "-prefix {}".format(self.package_folder)
        ]

        if self.options.get_safe("opengl") == "no":
            args += ["-no-opengl"]

        configure_script = os.path.join(self.source_folder, "qt5", "configure")

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

        for lib_name in (
            "DesignerComponents",
            "Designer",
            "Help",
            "Widgets",
            "OpenGL",
            "Core",
            "Svg",
            "Network",
            "PrintSupport",
            "MacExtras",
            "Multimedia",
            "MultimediaWidgets",
            "Concurrent",
            "Test",
            "Sql",
            "DBus",
            "XmlPatterns",
            "Xml",
            "Gui"
        ):
            lib_stem = f"libQt5{lib_name}"
            lib_file = f"{lib_stem}.{pkgconf.version}.dylib"

            # create fat lib
            inputs = [os.path.join(self.build_folder, arch, "INSTALL", "lib", lib_file) for arch in self.build_arches()]
            self.run(
                f"lipo -create -output {lib_file} {' '.join(inputs)}",
                cwd=lib_folder
            )

            # create fat lib file links
            dylib_version = pkgconf.version.split(".")
            self.run(
                f"ln -s {lib_file} {lib_stem}.{'.'.join(dylib_version[0:2])}.dylib",
                cwd=lib_folder
            )
            self.run(
                f"ln -s {lib_file} {lib_stem}.{'.'.join(dylib_version[0:1])}.dylib",
                cwd=lib_folder
            )

        for plugin in (
            os.path.join("audio", "libqtaudio_coreaudio.dylib"),
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
            os.path.join("mediaservice", "libqavfcamera.dylib"),
            os.path.join("mediaservice", "libqavfmediaplayer.dylib"),
            os.path.join("mediaservice", "libqtmedia_audioengine.dylib"),
            os.path.join("platforms", "libqcocoa.dylib",),
            os.path.join("platforms", "libqminimal.dylib",),
            os.path.join("platforms", "libqoffscreen.dylib",),
            os.path.join("platformthemes", "libqxdgdesktopportal.dylib",),
            os.path.join("playlistformats", "libqtmultimedia_m3u.dylib",),
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
