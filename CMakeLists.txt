cmake_minimum_required(VERSION 3.10)
project(toybox C)

# 设置C标准
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/generated/unstripped)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/generated/unstripped)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/generated/unstripped)

# 默认编译选项
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# 添加默认的编译标志
set(DEFAULT_CFLAGS 
    "-Wall" 
    "-Wundef" 
    "-Werror=implicit-function-declaration" 
    "-Wno-char-subscripts" 
    "-Wno-pointer-sign" 
    "-funsigned-char"
    "-Os"
    "-ffunction-sections"
    "-fdata-sections"
    "-fno-asynchronous-unwind-tables"
    "-fno-strict-aliasing"
)

# 添加编译选项
add_compile_options(${DEFAULT_CFLAGS})

# 查找Git并设置版本
find_package(Python3 REQUIRED)
find_package(Git)
if(GIT_FOUND AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
    execute_process(
        COMMAND ${GIT_EXECUTABLE} describe --tags --abbrev=12
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        OUTPUT_VARIABLE TOYBOX_VERSION
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    if(NOT TOYBOX_VERSION)
        set(TOYBOX_VERSION "0.8.13")
    endif()
else()
    set(TOYBOX_VERSION "0.8.13")
endif()

# 添加版本定义
add_definitions(-DTOYBOX_VERSION="${TOYBOX_VERSION}")

# 定义可构建的命令列表
set(TOYBOX_ALL_COMMANDS
    cat
    echo
    ls
    ps
    pwd
    rm
    cp
    mv
    touch
    mkdir
    rmdir
    chmod
    date
    sleep
    true
    false
    uname
    wc
    head
    tail
    sort
    uniq
    grep
    cut
    paste
    md5sum
    sha1sum
    base64
    hexdump
    od
    tee
    tr
    expr
    test
    seq
    fold
    who
    uptime
    free
    df
    du
)

# 如果没有指定要构建的命令，则默认启用所有命令
if(NOT DEFINED TOYBOX_ENABLE_ARGS)
    set(TOYBOX_ENABLE_ARGS "${TOYBOX_ALL_COMMANDS}")
endif()

# 将命令列表转换为分号分隔的格式
string(REPLACE " " ";" TOYBOX_ENABLE_ARGS "${TOYBOX_ENABLE_ARGS}")
string(REPLACE "," ";" TOYBOX_ENABLE_ARGS "${TOYBOX_ENABLE_ARGS}")

# 确保TOYBOX_ENABLE_ARGS是列表格式
# 重新解析参数，确保正确处理
separate_arguments(TOYBOX_ENABLE_ARGS)

# 创建默认配置（如果不存在）
set(CONFIG_FILE "${CMAKE_SOURCE_DIR}/.config")
if(NOT EXISTS ${CONFIG_FILE})
    # 创建配置文件内容
    set(CONFIG_CONTENT "# Default configuration for Toybox\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX=y\n")
    
    # 根据TOYBOX_ENABLE_ARGS设置命令的配置
    foreach(CMD ${TOYBOX_ALL_COMMANDS})
        list(FIND TOYBOX_ENABLE_ARGS ${CMD} CMD_INDEX)
        if(CMD_INDEX GREATER_EQUAL 0)
            # 将命令名转换为大写作为配置项
            string(TOUPPER ${CMD} CMD_UPPER)
            string(APPEND CONFIG_CONTENT "CONFIG_${CMD_UPPER}=y\n")
        else()
            string(TOUPPER ${CMD} CMD_UPPER)
            string(APPEND CONFIG_CONTENT "# CONFIG_${CMD_UPPER} is not set\n")
        endif()
    endforeach()
    
    # 添加其他配置选项
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_SELINUX is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_SMACK is not set\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_LSM_NONE=y\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_FLOAT=y\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_HELP=y\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_HELP_DASHDASH=y\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_ZHELP is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_FREE is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_NORECURSE is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_DEBUG is not set\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_SUID=y\n")
    string(APPEND CONFIG_CONTENT "CONFIG_TOYBOX_FORK=y\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_LIBCRYPTO is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_LIBZ is not set\n")
    string(APPEND CONFIG_CONTENT "# CONFIG_TOYBOX_FORCE_NOMMU is not set\n")
    
    file(WRITE ${CONFIG_FILE} ${CONFIG_CONTENT})
endif()

# 创建生成的头文件目录
file(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/generated)

# 生成所有配置头文件
add_custom_command(
    OUTPUT ${CMAKE_SOURCE_DIR}/generated/config.h ${CMAKE_SOURCE_DIR}/generated/newtoys.h ${CMAKE_SOURCE_DIR}/generated/flags.h ${CMAKE_SOURCE_DIR}/generated/options.h
    COMMAND python3 ${CMAKE_SOURCE_DIR}/scripts/gen_configs.py
    DEPENDS ${CONFIG_FILE}
    COMMENT "Generating config files from .config"
)

# 检测库依赖
set(LIBS "")
foreach(lib util crypt m resolv selinux smack attr crypto z log iconv tls ssl)
    find_library(${lib}_LIB ${lib})
    if(${lib}_LIB)
        list(APPEND LIBS ${${lib}_LIB})
    endif()
endforeach()

# 检测是否需要链接数学库
find_library(MATH_LIB m)
if(MATH_LIB)
    list(APPEND LIBS ${MATH_LIB})
endif()

# 获取启用的命令列表用于源文件
file(READ ${CONFIG_FILE} CONFIG_CONTENT)
string(REGEX REPLACE "\n" ";" CONFIG_LINES "${CONFIG_CONTENT}")

set(TOYBOX_CMD_SOURCES "")
set(TOYBOX_LIB_SOURCES
    lib/lib.c
    lib/xwrap.c
    lib/args.c
    lib/commas.c
    lib/dirtree.c
    lib/elf.c
    lib/env.c
    lib/hash.c
    lib/llist.c
    lib/net.c
    lib/password.c
    lib/portability.c
    lib/tty.c
    lib/utf8.c
    lib/deflate.c
    lib/tt_impl.c
)

# 根据启用的命令添加源文件
foreach(LINE ${CONFIG_LINES})
    if(LINE MATCHES "^CONFIG_([A-Za-z0-9_]+)=y$")
        string(REGEX MATCH "^CONFIG_([A-Za-z0-9_]+)=y$" MATCHED ${LINE})
        set(COMMAND_NAME ${CMAKE_MATCH_1})
        # 转换为小写用于文件名
        string(TOLOWER ${COMMAND_NAME} CMD_LOWER)
        # 只添加实际命令的源文件，跳过配置选项
        if(NOT ${COMMAND_NAME} MATCHES "^(TOYBOX_|SELINUX|SMACK|LSM|FLOAT|HELP|FREE|NORECURSE|DEBUG|SUID|FORK|LIB|FORCE|ZHELP|NOMMU)" AND NOT ${COMMAND_NAME} STREQUAL "TOYBOX")
            # 尝试在不同目录中查找命令源文件
            if(EXISTS "${CMAKE_SOURCE_DIR}/toys/posix/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/posix/${CMD_LOWER}.c")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/toys/lsb/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/lsb/${CMD_LOWER}.c")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/toys/other/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/other/${CMD_LOWER}.c")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/toys/android/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/android/${CMD_LOWER}.c")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/toys/example/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/example/${CMD_LOWER}.c")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/toys/pending/${CMD_LOWER}.c")
                list(APPEND TOYBOX_CMD_SOURCES "${CMAKE_SOURCE_DIR}/toys/pending/${CMD_LOWER}.c")
            endif()
        endif()
    endif()
endforeach()

message(STATUS "Enabled command sources: ${TOYBOX_CMD_SOURCES}")

# 创建库
add_library(toybox_lib ${TOYBOX_LIB_SOURCES})

# 设置库的包含路径
target_include_directories(toybox_lib PRIVATE
    ${CMAKE_BINARY_DIR}/generated
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/lib
)

# 为所有生成的头文件创建一个自定义目标
add_custom_target(generated_headers
    COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_SOURCE_DIR}/generated/globals.h
    COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_SOURCE_DIR}/generated/tags.h
    COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_SOURCE_DIR}/generated/help.h
    DEPENDS 
        ${CMAKE_SOURCE_DIR}/generated/config.h
        ${CMAKE_SOURCE_DIR}/generated/newtoys.h
        ${CMAKE_SOURCE_DIR}/generated/flags.h
)

# 主要的toybox可执行文件 - 使用原始main.c
add_executable(toybox
    main.c
    ${TOYBOX_CMD_SOURCES}
)

# 设置依赖
add_dependencies(toybox_lib generated_headers)
add_dependencies(toybox generated_headers)

# 设置可执行文件的包含路径
target_include_directories(toybox PRIVATE
    ${CMAKE_BINARY_DIR}/generated
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/lib
)

# 将lib库链接到toybox
target_link_libraries(toybox toybox_lib ${LIBS})

# 设置输出可执行文件名称
set_target_properties(toybox PROPERTIES OUTPUT_NAME toybox)

# 生成目录
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/generated)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/generated/unstripped)

# 安装规则
install(TARGETS toybox
    RUNTIME DESTINATION bin
)
