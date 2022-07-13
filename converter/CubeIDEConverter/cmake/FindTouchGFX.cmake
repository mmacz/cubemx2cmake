set(TOUCHGFX_ROOT ${CMAKE_SOURCE_DIR}/@TOUCHGFX_ROOT@)
set(TOUCHGFX_MIDDLEWARES_PATH ${CMAKE_SOURCE_DIR}/@TOUCHGFX_MIDDLEWARES@)

set(TOUCHGFX_PRECOMPILED_LIBRARY ${TOUCHGFX_MIDDLEWARES_PATH}/lib/core/cortex_@CORE@/gcc/libtouchgfx@HARD_FP@.a)
add_library(TouchGFX_Precompiled STATIC IMPORTED)
set_target_properties(TouchGFX_Precompiled PROPERTIES IMPORTED_LOCATION ${TOUCHGFX_PRECOMPILED_LIBRARY})

file(GLOB_RECURSE GFX_SOURCES
    "${TOUCHGFX_MIDDLEWARES_PATH}/framework/source/touchgfx/*.cpp"

    "${TOUCHGFX_ROOT}/gui/*.cpp"
    "${TOUCHGFX_ROOT}/generated/gui_generated/*.cpp"
    "${TOUCHGFX_ROOT}/generated/texts/src/*.cpp"
    "${TOUCHGFX_ROOT}/generated/fonts/src/*.cpp"
    "${TOUCHGFX_ROOT}/generated/images/src/*.cpp"
)

add_library(TouchGFX STATIC)
target_compile_options(TouchGFX PRIVATE ${CORE_FLAGS})
target_sources(TouchGFX 
    PRIVATE
        ${GFX_SOURCES}
)
target_include_directories(TouchGFX
    PUBLIC
        ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include
        ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/common
        ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/mvp
        ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/touchgfx
        
        ${TOUCHGFX_ROOT}/gui/include
        ${TOUCHGFX_ROOT}/generated/gui_generated/include
        ${TOUCHGFX_ROOT}/generated/texts/include
        ${TOUCHGFX_ROOT}/generated/fonts/include
        ${TOUCHGFX_ROOT}/generated/images/include
)
target_link_libraries(TouchGFX PUBLIC TouchGFX_Precompiled)
add_library(ST::TouchGFX ALIAS TouchGFX)
