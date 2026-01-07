# toys/pending/CMakeLists.txt
# Pending (unfinished) utilities for toybox

# Collect all source files
file(GLOB PENDING_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${PENDING_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(PENDING_TOY_${toy_name}_SRC ${source_file})
    set(PENDING_TOY_${toy_name}_SRC ${PENDING_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()