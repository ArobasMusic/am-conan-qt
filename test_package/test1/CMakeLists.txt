project(test1)

add_executable(${PROJECT_NAME} main.cc)
target_compile_features(${PROJECT_NAME}
    PRIVATE
        cxx_nullptr
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        Qt5::Core
)

if(NOT MSVC)
    set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES
            COMPILE_FLAGS "-fPIC"
    )
endif()

# CTest is a testing tool that can be used to test your project.
add_test(
    NAME CMake-Qt-Target
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    COMMAND $<TARGET_FILE:${PROJECT_NAME}>
)
