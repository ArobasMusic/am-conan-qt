Conan package for Qt
---------------------

[Conan.io](https://conan.io) package for [Qt](https://www.qt.io) library.

## Basic setup
```
$ conan search "Qt/*" -r arobasmusic
Qt/5.9.9-7@arobasmusic/stable
Qt/5.12.8-2@arobasmusic/stable
Qt/5.15.1-2@arobasmusic/stable
Qt/6.0.0-1@arobasmusic/stable
```

```
$ conan install "Qt/5.12.8-1@arobasmusic/stable" -r arobasmusic
```

## Project setup
If you handle multiple dependencies in your project is better to add a *conanfile.txt*

```
[requires]
Qt/6.0.0-1@arobasmusic/stable

[generators]
cmake
cmake_paths
```

## Options

* `framework` - _macOS only_
    - `False` _default_ - will build dylib only,
    - `True` - will build frameworks.
