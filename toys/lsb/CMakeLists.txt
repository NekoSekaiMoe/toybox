# toys/lsb/CMakeLists.txt
# LSB (Linux Standard Base) utilities for toybox

# Collect all source files
file(GLOB LSB_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${LSB_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(LSB_TOY_${toy_name}_SRC ${source_file})
    set(LSB_TOY_${toy_name}_SRC ${LSB_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()