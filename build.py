import os
import platform

from conanio.packager import ConanMultiPackager

from conans.client.loader import parse_conanfile
from conans.client.graph.python_requires import ConanPythonRequire

def build():
    builder = ConanMultiPackager(
        build_policy="missing",
        username="arobasmusic"
    )
    builder.add_common_builds()
    if platform.system() == "Darwin":
        os_versions = os.getenv("CONAN_OS_VERSIONS", "").strip()

        if len(os_versions) != 0:
            builds = []
            for settings, options, env_vars, build_requires, reference in builder.items:
                for os_version in map(lambda version: version.strip(), os_versions.split(',')):
                    builds.append([
                        {**settings, "os.version": os_version},
                        options,
                        env_vars,
                        build_requires,
                        reference
                    ])
            builder.builds = builds
    builder.run()

if __name__ == "__main__":
    build()
