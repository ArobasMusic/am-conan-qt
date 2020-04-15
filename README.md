Conan package for Qt
--------------------------------------------

[Conan.io](https://conan.io) package for [Qt](https://www.qt.io) library.
This package includes by default the Qt Base module (Core, Gui, Widgets,
Network, ...). Others modules can be added using options.

## Basic setup

```
$ conan search "Qt/*" -r arobasmusic
Qt/5.9.8-4@arobasmusic/testing
Qt/5.9.8-53@arobasmusic/stable
Qt/5.12.5-5@arobasmusic/testing
Qt/5.12.8-13@arobasmusic/testing
Qt/5.12.8-1@arobasmusic/stable

$ conan install "Qt/5.12.8-1@arobasmusic/stable" -r arobasmusic
```

## Options

* `canvas3d` - `True`, `False` - enable/disable _canvas4d_ _Qt_ module,
* `connectivity` - `True`, `False` - enable/disable _connectivity_ _Qt_ module,
* `gamepad` - `True`, `False` - enable/disable _gamepad_ _Qt_ module,
* `graphicaleffects` - `True`, `False` - enable/disable _graphicaleffects_ _Qt_ module,
* `location` - `True`, `False` - enable/disable _location_ _Qt_ module,
* `serialport` - `True`, `False` - enable/disable _serialport_ _Qt_ module,
* `tools` - `True`, `False` - enable/disable _tools_ _Qt_ module,
* `webengine` - `True`, `False` - enable/disable _webengine_ _Qt_ module,
* `websockets` - `True`, `False` - enable/disable _websockets_ _Qt_ module.

### Windows specific options
* `opengl` - possible values are:
    - `"desktop"`,
    - `"dynamic"`.

* `openssl` - possible values are:
    - `"no"`,
    - `"yes"`,
    - `"linked"`.

### Windows specific options
* `framework`
    - `True`, will build frameworks,
    - `False`, will build dylib only.

## Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

```
    [requires]
    Qt/5.12.8-1@arobasmusic/stable

    [options]
    Qt:shared=true # false
    # On Windows, you can choose the opengl mode, default is 'desktop'
    Qt:opengl=desktop # dynamic
    # On Windows, you can choose to enable/disable openssl support, default is 'no'
    Qt:openssl=yes
    # If you need specific Qt modules, you can add them as follow:
    Qt:websockets=true
    Qt:xmlpatterns=true

    [generators]
    txt
    cmake
```
