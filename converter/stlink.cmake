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
