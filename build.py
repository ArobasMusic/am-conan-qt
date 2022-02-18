import platform

from conanio.packager import ConanMultiPackager, split_colon_env

def build():
    builder = ConanMultiPackager(
        build_policy="missing",
        username="arobasmusic"
    )

    if platform.system() == "Darwin":
        builder.add_common_builds(build_all_options_values=["Overloud:universalbinary"])

        if os_versions := split_colon_env("CONAN_OS_VERSIONS"):
            builds = []
            for settings, options, env_vars, build_requires, reference in builder.items:
                for os_version in os_versions:
                    builds.append([
                        {**settings, "os.version": os_version},
                        options,
                        env_vars,
                        build_requires,
                        reference,
                    ])
            builder.builds = builds
    else:
        builder.add_common_builds()

    builder.run()

if __name__ == "__main__":
    build()
