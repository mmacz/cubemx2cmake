cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/armv7-toolchain.cmake)
set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/@LINKER_SCRIPT@)

project(@PROJECT@
    VERSION 1.0.0
    LANGUAGES ASM C CXX
)

include(stlink.cmake)

file(GLOB_RECURSE CPP_SOURCES "Src/*.cpp")

add_executable(@PROJECT@.elf)
target_sources(@PROJECT@.elf
    PRIVATE
        # C sources
@SOURCES@

        # CPP sources
        ${CPP_SOURCES}

        # Startup file
        @STARTUP@
)
target_include_directories(@PROJECT@.elf 
    PUBLIC
@INCLUDES@
)

target_compile_definitions(@PROJECT@.elf PUBLIC
    @C_DEFS@ -D__weak=__attribute__\(\(weak\)\) -D__packed=__attribute__\(\(__packed__\)\)
)

target_compile_options(@PROJECT@.elf PRIVATE @CFLAGS@ -ffunction-sections -fdata-sections -Wall)
target_link_options(@PROJECT@.elf PRIVATE @CFLAGS@ -specs=nano.specs -Wl,--gc-sections -T${LINKER_SCRIPT} -Wl,-Map=${PROJECT_BINARY_DIR}/HelloWorld.map,--cref)

target_link_libraries(@PROJECT@.elf 
    PRIVATE
@LIBS@
)

add_custom_command(TARGET @PROJECT@.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} ARGS -Oihex $<TARGET_FILE:@PROJECT@.elf> ${CMAKE_BINARY_DIR}/@PROJECT@.hex
    COMMAND ${CMAKE_OBJCOPY} ARGS -Obinary $<TARGET_FILE:@PROJECT@.elf> ${CMAKE_BINARY_DIR}/@PROJECT@.bin
    COMMENT "Create intel hex and binary files"
)

add_custom_command(TARGET @PROJECT@.elf POST_BUILD
    COMMAND ${CMAKE_SIZE} @PROJECT@.elf
)
