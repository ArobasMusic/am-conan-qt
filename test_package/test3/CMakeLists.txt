project(test3)

find_package(Qt6Widgets REQUIRED)

set(CMAKE_AUTOUIC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(AUTOMOC_MOC_OPTIONS PROPERTIES FOLDER CMakeAutomocTargets)
set_property(GLOBAL PROPERTY AUTOMOC_FOLDER CMakeAutomocTargets)

add_executable(${PROJECT_NAME}
    main.cc
    mainwindow.cc
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        Qt6::Widgets
)

# CTest is a testing tool that can be used to test your project.
add_test(
    NAME Widgets
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    COMMAND $<TARGET_FILE:${PROJECT_NAME}>
)
