# lib/CMakeLists.txt
# Library files for toybox

set(LIB_SOURCES
    args.c
    commas.c
    deflate.c
    dirtree.c
    elf.c
    env.c
    hash.c
    lib.c
    llist.c
    net.c
    password.c
    portability.c
    tty.c
    utf8.c
    xwrap.c
)

add_library(toybox_lib STATIC ${LIB_SOURCES})

# 设置头文件目录
target_include_directories(toybox_lib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${CMAKE_BINARY_DIR}/generated
)

# 添加编译定义
target_compile_definitions(toybox_lib PUBLIC
    TOYBOX_VERSION="${TOYBOX_VERSION}"
)