cmake_minimum_required(VERSION 3.15)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR armv7hf)

set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_CXX_COMPILER arm-none-eabi-g++)
set(CMAKE_ASM_COMPILER ${CMAKE_C_COMPILER})
set(CMAKE_AR arm-none-eabi-ar)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy)
set(CMAKE_OBJDUMP arm-none-eabi-objdump)
set(CMAKE_SIZE arm-none-eabi-size)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/@LINKER_SCRIPT@)

project(@PROJECT@
    VERSION 1.0.0
    LANGUAGES ASM C CXX
)

add_executable(@PROJECT@.elf)
target_sources(@PROJECT@.elf
    PRIVATE
        # C sources
@SOURCES@

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
