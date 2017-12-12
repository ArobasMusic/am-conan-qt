from conan.packager import ConanMultiPackager

def build():
    builder = ConanMultiPackager(username="amusic", channel="stable")
    builder.add_common_builds()
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["compiler"] == "Visual Studio":
            if settings["compiler.runtime"] == "MT" or settings["compiler.runtime"] == "MTd":
                # Ignore MT runtime
                continue
        filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()

if __name__ == "__main__":
    build()
