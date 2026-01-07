# toys/posix/CMakeLists.txt
# POSIX utilities for toybox

# 收集所有源文件
set(POSIX_TOYS_SOURCES
    basename.c
    cal.c
    cat.c
    chgrp.c
    chmod.c
    cksum.c
    cmp.c
    comm.c
    cp.c
    cpio.c
    cut.c
    date.c
    dd.c
    df.c
    dirname.c
    du.c
    echo.c
    env.c
    expand.c
    false.c
    file.c
    find.c
    fold.c
    getconf.c
    grep.c
    head.c
    iconv.c
    id.c
    kill.c
    link.c
    ln.c
    logger.c
    ls.c
    mkdir.c
    mkfifo.c
    nice.c
    nl.c
    nohup.c
    od.c
    paste.c
    patch.c
    printf.c
    ps.c
    pwd.c
    renice.c
    rm.c
    rmdir.c
    sed.c
    sleep.c
    sort.c
    split.c
    strings.c
    tail.c
    tar.c
    tee.c
    test.c
    time.c
    touch.c
    true.c
    tsort.c
    tty.c
    ulimit.c
    uname.c
    uniq.c
    unlink.c
    uudecode.c
    uuencode.c
    wc.c
    who.c
    xargs.c
)

# 为每个源文件创建一个可执行文件，但只有在配置启用时才真正构建
foreach(source_file ${POSIX_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    # 我们将这些源文件作为可能的组件添加，实际包含将由配置决定
    set(POSIX_TOY_${toy_name}_SRC ${source_file})
    set(POSIX_TOY_${toy_name}_SRC ${POSIX_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()