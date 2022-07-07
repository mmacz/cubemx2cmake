add_custom_target(Chip-Erase
    COMMAND st-flash --connect-under-reset erase
    COMMENT "Erasing chip"
)

add_custom_target(Chip-Flash
    COMMAND st-flash --connect-under-reset erase
    COMMAND st-flash --connect-under-reset --reset --flash=@FLASH_SIZE@ write ${CMAKE_BINARY_DIR}/@PROJECT@.bin @FLASH_ORIGIN@
    COMMENT "Flash chip with @PROJECT@.bin"
    DEPENDS @PROJECT@.elf
)

add_custom_target(Chip-Debug
    COMMAND st-util --listen_port 2331
    COMMAND ${DEBUGGER} -tui -command target remote localhost:2331 ${CMAKE_BINARY_DIR}/@PROJECT@.bin
    COMMENT "Debug target application"
    DEPENDS @PROJECT@.elf
)

add_custom_target(Debug-Server
    COMMAND st-util --listen_port 2331
    DEPENDS @PROJECT@.elf
)