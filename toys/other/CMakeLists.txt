# toys/other/CMakeLists.txt
# Other utilities for toybox

# Collect all source files
file(GLOB OTHER_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${OTHER_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(OTHER_TOY_${toy_name}_SRC ${source_file})
    set(OTHER_TOY_${toy_name}_SRC ${OTHER_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()