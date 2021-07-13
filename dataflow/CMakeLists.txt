#######################1.create project
cmake_minimum_required(VERSION 2.8.7)
if(POLICY CMP0046)
  cmake_policy(SET CMP0046 NEW)
endif()
if(POLICY CMP0054)
  cmake_policy(SET CMP0054 NEW)
endif()

project(RECOMMAND_INFER C CXX)


# --[ Options
option(RELEASE "Build type" ON)
option(build_tests "build recommand infer unit test" ON)
option(with_pybind11 "build with pybind11" OFF)

if(RELEASE)
  set(CMAKE_BUILD_TYPE RELEASE)
else()
  set(CMAKE_BUILD_TYPE DEBUG)
endif()

set(CMAKE_CXX_FLAGS "-fPIC -Wall -Werror -std=c++11")
set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g2 -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -DNDEBUG -O3")


# add head file search path
include_directories(${PROJECT_SOURCE_DIR}/module/src/)
include_directories(${PROJECT_SOURCE_DIR}/include)
            
# add sub dir
if(with_pybind11)
  add_subdirectory(${PROJECT_SOURCE_DIR}/include/pybind11)
endif()

add_subdirectory(modules)

