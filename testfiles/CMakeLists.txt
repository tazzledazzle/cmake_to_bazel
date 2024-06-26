cmake_minimum_required(VERSION 3.10)

project(SimpleProject)

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Add an executable target
add_executable(MyApp src/main.cpp src/helper.cpp)

# Add a library target
add_library(MyLib src/lib.cpp)

# Link the library to the executable
target_link_libraries(MyApp MyLib)
