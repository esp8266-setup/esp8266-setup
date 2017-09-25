# %project% library

This a library to be used in firmware for the ESP8266.

## What is this

**TODO**

## Usage instructions

This library is built with the [esp8266-setup](http://github.com/esp8266-setup/esp8266-setup) tool in mind.

If you are already using the `esp8266-setup` build system just issue the following command in your project dir:

```bash
esp8266-setup add-library %url%
```

If you do not want to use the `esp8266-setup` build system just grab the files from the `src` and `include` directories and add them to your project.

Be aware that most libraries built with this build system use the `C99` standard, so you may have to add `--std=c99` to your `CFLAGS`.

## Build instructions

- Install the ESP8266 Toolchain
- Download the ESP8266 RTOS SDK
- Compile the library: 
```bash
    make \
      XTENSA_TOOLS_ROOT=/path/to/compiler/bin \
      SDK_PATH=/path/to/ESP8266_RTOS_SDK
```

- The finished library will be placed in the current directory under the name
  of `lib%project%.a`
- Corresponding include files are in `include/`

If you installed the ESP SDK and toolchain to a default location (see below) you may just type `make` to build.

### Default locations

#### Windows

- **XTENSA\_TOOLS\_ROOT**: `c:\ESP8266\xtensa-lx106-elf\bin`
- **SDK_PATH**: `c:\ESP8266\ESP8266_RTOS_SDK`

#### MacOS X

We assume that your default file system is not case sensitive so you will have created a sparse bundle with a case sensitive filesystem which is named `ESP8266`:

- **XTENSA\_TOOLS\_ROOT**: `/Volumes/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin`
- **SDK_PATH**: `/Volumes/ESP8266/ESP8266_RTOS_SDK`

#### Linux

- **XTENSA\_TOOLS\_ROOT**: `/opt/Espressif/crosstool-NG/builds/xtensa-lx106-elf/bin`
- **SDK_PATH**: `/opt/Espressif/ESP8266_RTOS_SDK`
