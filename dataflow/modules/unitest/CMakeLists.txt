if(build_tests)
  set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

  include_directories(${include_path})
  link_directories("${PROJECT_SOURCE_DIR}/lib")
  list(APPEND INFER_LIBS ${PROJECT_SOURCE_DIR}/lib/libcnstream-toolkit.so)

  file(GLOB_RECURSE ranking_test_srcs ${PROJECT_SOURCE_DIR}/modules/unitest/ranking_test.cpp)
  add_executable(ranking_test ${ranking_test_srcs})
  target_link_libraries(ranking_test dataflow ${INFER_LIBS})

  file(GLOB_RECURSE ranking_perf_srcs ${PROJECT_SOURCE_DIR}/modules/unitest/ranking_perf.cpp)
  add_executable(ranking_perf ${ranking_perf_srcs})
  target_link_libraries(ranking_perf dataflow ${INFER_LIBS})
endif()
