add_custom_command(OUTPUT bench.cpp
        COMMAND souffle ${CMAKE_CURRENT_SOURCE_DIR}/rules.small.dl -w -t explain -o bench
        DEPENDS rules.small.dl)

add_library(animals SHARED bench.cpp handle.cpp)
target_compile_options(animals PRIVATE -D__EMBEDDED_SOUFFLE__ -march=native -fPIC -O3)
set_target_properties(animals PROPERTIES OUTPUT_NAME bench)

add_custom_command(TARGET animals POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_BINARY_DIR})