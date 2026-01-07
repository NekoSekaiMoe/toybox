# toys/CMakeLists.txt
# Individual toy applications

# 添加所有子目录
add_subdirectory(android)
add_subdirectory(example)
add_subdirectory(lsb)
add_subdirectory(net)
add_subdirectory(other)
add_subdirectory(pending)
add_subdirectory(posix)

# 默认情况下，我们创建一个目标来收集所有可能的源文件
# 但实际包含哪些文件将由配置文件决定