cmake_minimum_required (VERSION 3.10)

project (GenPng)

set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set (src_dir "./src/")

set (dep_lib "D:/mingw64/lib")

file (GLOB src_files "${src_dir}/*.cpp")

include_directories ("./include/")

include_directories ("D:/mingw64/include")

add_executable (out ${src_files})

link_directories ("D:/mingw64/lib")

