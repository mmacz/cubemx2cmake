set(TOUCHGFX_ROOT ${CMAKE_SOURCE_DIR}/@TOUCHGFX_ROOT@)
set(TOUCHGFX_MIDDLEWARES_PATH ${CMAKE_SOURCE_DIR}/@TOUCHGFX_MIDDLEWARES@)

list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include)
list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/common)
list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/mvp)
list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/platform)
list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/platform/driver/lcd)
list(APPEND TOUCHGFX_FRAMEWORK_INCLUDE_DIRS ${TOUCHGFX_MIDDLEWARES_PATH}/framework/include/touchgfx)
set(TOUCHGFX_FRAMEWORK_LIBRARY ${TOUCHGFX_MIDDLEWARES_PATH}/lib/core/cortex_@CORE@/gcc/libtouchgfx@HARD_FP@.a)

add_library(TouchGFX_Framework STATIC IMPORTED)
set_target_properties(TouchGFX_Framework PROPERTIES IMPORTED_LOCATION ${TOUCHGFX_FRAMEWORK_LIBRARY})
set_target_properties(TouchGFX_Framework PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${TOUCHGFX_FRAMEWORK_INCLUDE_DIRS}")


file(GLOB_RECURSE GFX_SOURCES
    "${TOUCHGFX_ROOT}/generated/fonts/*.cpp"
    "${TOUCHGFX_ROOT}/generated/gui_generated/*.cpp"
    "${TOUCHGFX_ROOT}/generated/images/*.cpp"
    "${TOUCHGFX_ROOT}/generated/texts/*.cpp"
    "${TOUCHGFX_ROOT}/gui/*.cpp"
)
add_library(TouchGFX STATIC)
target_compile_options(TouchGFX PRIVATE ${CORE_FLAGS} -specs=nano.specs)
target_sources(TouchGFX 
    PRIVATE
        ${GFX_SOURCES}
)
target_include_directories(TouchGFX
    PUBLIC
        ${TOUCHGFX_ROOT}/gui/include
        ${TOUCHGFX_ROOT}/generated/fonts/include
        ${TOUCHGFX_ROOT}/generated/gui_generated/include
        ${TOUCHGFX_ROOT}/generated/images/include
        ${TOUCHGFX_ROOT}/generated/texts/include
)
target_link_libraries(TouchGFX PUBLIC TouchGFX_Framework)
add_library(ST::TouchGFX ALIAS TouchGFX)
