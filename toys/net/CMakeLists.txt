# toys/net/CMakeLists.txt
# Network utilities for toybox

# Collect all source files
file(GLOB NET_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${NET_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(NET_TOY_${toy_name}_SRC ${source_file})
    set(NET_TOY_${toy_name}_SRC ${NET_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()