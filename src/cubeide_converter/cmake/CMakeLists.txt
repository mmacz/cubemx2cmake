cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/cmake/@TOOLCHAIN_FILE@)
set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/@LINKER_SCRIPT@)

project(@PROJECT@
    VERSION 1.0.0
    LANGUAGES ASM C CXX
)

add_compile_options(
    ${CORE_FLAGS} 
    -ffunction-sections
    -fdata-sections
    -Wall
)
add_definitions(
    @C_DEFS@ 
    -D__weak=__attribute__\(\(weak\)\) 
    -D__packed=__attribute__\(\(__packed__\)\)
)

list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
include(stlink)
find_package(STDrivers REQUIRED)
@TOUCHGFX_START@
set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} -fno-rtti)
find_package(TouchGFX REQUIRED)
@TOUCHGFX_END@
# Custom modules start
# Custom modules end

file(GLOB_RECURSE STARTUP_FILE "Core/*.s")
add_executable(@PROJECT@.elf)
target_sources(@PROJECT@.elf
    PRIVATE
        # ASM
        ${STARTUP_FILE}

        # Sources C + Cpp
        @PROJECT_SOURCES@
)
target_include_directories(@PROJECT@.elf 
    PUBLIC
        @PROJECT_INC_DIRS@
)
target_link_options(@PROJECT@.elf 
    PRIVATE
    ${CORE_FLAGS} -T${LINKER_SCRIPT}
    -Wl,--gc-sections -Wl,-Map=${PROJECT_BINARY_DIR}/@PROJECT@.map,--cref
)

target_link_libraries(@PROJECT@.elf 
    PRIVATE
        c
        m
        nosys
        ST::Drivers@TOUCHGFX_LIB@
        # Custom libraries link start
        # Custom libraries linke end
)

add_custom_command(TARGET @PROJECT@.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} ARGS -Oihex $<TARGET_FILE:@PROJECT@.elf> ${CMAKE_BINARY_DIR}/@PROJECT@.hex
    COMMAND ${CMAKE_OBJCOPY} ARGS -Obinary $<TARGET_FILE:@PROJECT@.elf> ${CMAKE_BINARY_DIR}/@PROJECT@.bin
    COMMENT "Create intel hex and binary files"
)

add_custom_command(TARGET @PROJECT@.elf POST_BUILD
    COMMAND ${CMAKE_SIZE} @PROJECT@.elf
)
