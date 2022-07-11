cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/armv7-toolchain.cmake)
set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/@LINKER_SCRIPT@)

project(@PROJECT@
    VERSION 1.0.0
    LANGUAGES ASM C CXX
)

include(stlink.cmake)

add_executable(@PROJECT@.elf)
target_sources(@PROJECT@.elf
    PRIVATE
        # ASM sources
        @ASM_SOURCES@

        # C sources
        @C_SOURCES@

        # Cpp sources
        @CPP_SOURCES@
)
target_include_directories(@PROJECT@.elf 
    PUBLIC
        @INC_DIRS@
)

target_compile_definitions(@PROJECT@.elf
    PUBLIC
        @C_DEFS@ 
        -D__weak=__attribute__\(\(weak\)\) 
        -D__packed=__attribute__\(\(__packed__\)\)
)


target_compile_options(@PROJECT@.elf PRIVATE @CFLAGS@ -ffunction-sections -fdata-sections -Wall)
target_link_options(@PROJECT@.elf PRIVATE @LDFLAGS@  -T${LINKER_SCRIPT} -specs=nano.specs -Wl,--gc-sections -Wl,-Map=${PROJECT_BINARY_DIR}/@PROJECT@.map,--cref)

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
