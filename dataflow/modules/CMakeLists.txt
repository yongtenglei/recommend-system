set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

include_directories(${PROJECT_SOURCE_DIR}/include/)

set(module_list model_runner ranking)

if(with_pybind11)
  list(APPEND module_list python)
endif()

foreach(module ${module_list})
  include_directories(${PROJECT_SOURCE_DIR}/modules/${module}/include)
  file(GLOB_RECURSE module_src ${PROJECT_SOURCE_DIR}/modules/${module}/*.cpp)
  list(APPEND srcs ${module_src})
endforeach()

if(with_pybind11)
  pybind11_add_module(dataflow SHARED ${srcs})
  set(EASYSDK_LIBS ${PROJECT_SOURCE_DIR}/lib/libcnstream-toolkit.so)
  target_link_libraries(dataflow ${EASYSDK_LIBS})
else()
  add_library(dataflow SHARED ${srcs})
  set(EASYSDK_LIBS ${PROJECT_SOURCE_DIR}/lib/libcnstream-toolkit.so)
  target_link_libraries(dataflow ${EASYSDK_LIBS})
  if(build_tests)
    add_subdirectory(unitest)
  endif()
endif()
