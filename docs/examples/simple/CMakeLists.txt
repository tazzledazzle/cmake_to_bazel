cmake_minimum_required(VERSION 3.10)
project(SimpleExample)

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Add an executable target
add_executable(SimpleApp src/main.cpp src/helper.cpp)

# Add a library target
add_library(SimpleLib src/lib.cpp)

# Link the library to the executable
target_link_libraries(SimpleApp SimpleLib)