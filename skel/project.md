# %project%

This is the %project% firmware for the ESP8266.

## What is this

**TODO**

## Schematic

**TODO**

## Build instructions

- Install the ESP8266 Toolchain
- Download the ESP8266 RTOS SDK
- Compile the firmware: 
```bash
    make \
      XTENSA_TOOLS_ROOT=/path/to/compiler/bin \
      SDK_PATH=/path/to/ESP8266_RTOS_SDK \
      ESPTOOL=/path/to/esptool.py
```

- The firmware build will be in `./firmware/`
- Flash the firmware with `esptool.py`

By default this build system compiles firmware for the use with a bootloader.
If the selected linker script allows, two firmware images are built to make OTA updating feasible. If there are 2 MegaBytes of flash available only one firmware image will be build which can be used for either slot.

If you installed the ESP SDK and toolchain to a default location (see below) you may just type `make` to build.

### Default locations

We do not use the default location of the `esptool.py` because it may happen that you want to have a virtual env for your python installation to install additional packages like pyserial etc.

We assume you copied the `esptool.py` and changed the shebang line to point to a virtualenv. Because it would be probably unwise to change the original we assume a copy in a generic `/bin` directory.

#### Windows

- **XTENSA\_TOOLS\_ROOT**: `c:\ESP8266\xtensa-lx106-elf\bin`
- **SDK_PATH**: `c:\ESP8266\ESP8266_RTOS_SDK`
- **ESPTOOL**: `c:\ESP8266\bin\esptool.py`

#### MacOS X

We assume that your default file system is not case sensitive so you will have created a sparse bundle with a case sensitive filesystem which is named `ESP8266`:

- **XTENSA\_TOOLS\_ROOT**: `/Volumes/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin`
- **SDK_PATH**: `/Volumes/ESP8266/ESP8266_RTOS_SDK`
- **ESPTOOL**: `/Volumes/ESP8266/bin/esptool.py`

#### Linux

- **XTENSA\_TOOLS\_ROOT**: `/opt/Espressif/crosstool-NG/builds/xtensa-lx106-elf/bin`
- **SDK_PATH**: `/opt/Espressif/ESP8266_RTOS_SDK`
- **ESPTOOL**: `/opt/Espressif/bin/esptool.py`
