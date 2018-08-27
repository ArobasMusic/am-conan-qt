cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(APPLE)
    # Workaround for rpath error
    set(CMAKE_SKIP_RPATH 0)
endif(APPLE)

configure_file(qt.conf.in ${CMAKE_BINARY_DIR}/bin/qt.conf)

find_package(Qt5Core REQUIRED)

set(CMAKE_AUTOMOC ON)
set(AUTOMOC_MOC_OPTIONS PROPERTIES FOLDER CMakeAutomocTargets)
set_property(GLOBAL PROPERTY AUTOMOC_FOLDER CMakeAutomocTargets)

enable_testing()

if(WIN32)
    file(TO_NATIVE_PATH ${CONAN_BIN_DIRS_QT} QT_LIB_DIR)
else()
    set(QT_LIB_DIR CONAN_LIB_DIRS_QT)
endif()

add_subdirectory(test1)
add_subdirectory(test2)
# add_subdirectory(test3)
