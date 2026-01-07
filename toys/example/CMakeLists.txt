# toys/example/CMakeLists.txt
# Example utilities for toybox

# Collect all source files
file(GLOB EXAMPLE_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${EXAMPLE_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(EXAMPLE_TOY_${toy_name}_SRC ${source_file})
    set(EXAMPLE_TOY_${toy_name}_SRC ${EXAMPLE_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()