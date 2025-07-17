cmake_minimum_required(VERSION 3.10)
project(AdvancedExample)

# Set variables
set(SOURCES src/main.cpp src/helper.cpp src/utils.cpp)
set(LIB_SOURCES src/lib.cpp src/lib_utils.cpp)
set(ENABLE_TESTS ON)
set(BUILD_SHARED_LIBS OFF)

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/third_party/include
)

# Add compile definitions
add_compile_definitions(VERSION="1.0.0")

# Conditional compilation
if(ENABLE_TESTS)
    add_compile_definitions(ENABLE_TESTS)
endif()

# Library type based on variable
if(BUILD_SHARED_LIBS)
    add_library(AdvancedLib SHARED ${LIB_SOURCES})
else()
    add_library(AdvancedLib STATIC ${LIB_SOURCES})
endif()

# Target-specific include directories
target_include_directories(AdvancedLib PRIVATE
    ${PROJECT_SOURCE_DIR}/src/internal
)

# Target-specific compile options
target_compile_options(AdvancedLib PRIVATE
    -Wall
    -Werror
)

# Main executable
add_executable(AdvancedApp ${SOURCES})

# Link libraries
target_link_libraries(AdvancedApp
    AdvancedLib
    pthread
    dl
)

# Conditional test executable
if(ENABLE_TESTS)
    add_executable(AdvancedTests tests/test_main.cpp tests/test_lib.cpp)
    target_link_libraries(AdvancedTests AdvancedLib)
endif()

# Custom command
add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/generated.h
    COMMAND ${CMAKE_COMMAND} -E echo "#define GENERATED 1" > ${CMAKE_CURRENT_BINARY_DIR}/generated.h
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.json
)

# Custom target
add_custom_target(
    generate_headers
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/generated.h
)