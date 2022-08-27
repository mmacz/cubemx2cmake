add_library(STDrivers STATIC)
target_compile_options(STDrivers PRIVATE ${CORE_FLAGS})
target_sources(STDrivers
    PRIVATE

    # Driver sources
        @DRIVER_SOURCES@
)
target_include_directories(STDrivers
    PUBLIC
        @DRIVER_INC_DIRS@
)
add_library(ST::Drivers ALIAS STDrivers)
