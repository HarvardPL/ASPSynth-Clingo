#!/usr/bin/env python3

import os
import sys

text = lambda name : \
f"""add_custom_command(OUTPUT bench.cpp
        COMMAND souffle ${{CMAKE_CURRENT_SOURCE_DIR}}/rules.small.dl -w -t explain -o bench
        DEPENDS rules.small.dl)

add_library({name} SHARED bench.cpp handle.cpp)
target_compile_options({name} PRIVATE -D__EMBEDDED_SOUFFLE__ -march=native -fPIC -O3)
set_target_properties({name} PROPERTIES OUTPUT_NAME bench)

add_custom_command(TARGET {name} POST_BUILD
        COMMAND ${{CMAKE_COMMAND}} -E copy_directory
        ${{CMAKE_CURRENT_SOURCE_DIR}}
        ${{CMAKE_CURRENT_BINARY_DIR}})"""


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} BENCH_DIR")
        exit(1)
    bmdir = sys.argv[1]
    if not os.path.isdir(bmdir):
        print(f"{bmdir} is not a directory")
        exit(1)
    name = os.path.basename(os.path.normpath(bmdir))
    with open(os.path.join(bmdir, "CMakeLists.txt"), "w") as f:
        f.write(text(name))


if __name__ == "__main__":
    main()
