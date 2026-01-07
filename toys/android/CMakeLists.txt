# toys/android/CMakeLists.txt
# Android-specific utilities for toybox

# Collect all source files
file(GLOB ANDROID_TOYS_SOURCES
    *.c
)

# Add each source as a potential component
foreach(source_file ${ANDROID_TOYS_SOURCES})
    get_filename_component(toy_name ${source_file} NAME_WE)
    
    set(ANDROID_TOY_${toy_name}_SRC ${source_file})
    set(ANDROID_TOY_${toy_name}_SRC ${ANDROID_TOY_${toy_name}_SRC} PARENT_SCOPE)
endforeach()