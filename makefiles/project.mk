# Copyright 2017 Johannes Schriewer <hallo@dunkelstern.de>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# OS-Detection
ifeq ($(OS),Windows_NT)
    OS = Windows
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        OS = Linux
    endif
    ifeq ($(UNAME_S),Darwin)
        OS = Darwin
    endif
endif

# base directory for the compiler
# base directory of the ESP8266 SDK package, absolute
# serial port to use for flashing
# esptool.py path
ifeq ($(OS),Windows)
    XTENSA_TOOLS_ROOT ?= /c/ESP8266/xtensa-lx106-elf/bin
    SDK_PATH          ?= /c/ESP8266/ESP8266_RTOS_SDK
    SERIALPORT        ?= COM3
    ESPTOOL		      ?= /c/ESP8266/bin/esptool.py
endif
ifeq ($(OS),Darwin)
    XTENSA_TOOLS_ROOT ?= /Volumes/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin
    SDK_PATH          ?= /Volumes/ESP8266/ESP8266_RTOS_SDK
    SERIALPORT        ?= /dev/tty.usbserial
    ESPTOOL		      ?= /Volumes/ESP8266/bin/esptool.py
endif
ifeq ($(OS),Linux)
    XTENSA_TOOLS_ROOT ?= /opt/Espressif/crosstool-NG/builds/xtensa-lx106-elf/bin
    SDK_PATH          ?= /opt/Espressif/ESP8266_RTOS_SDK
    SERIALPORT        ?= /dev/ttyUSB0
    ESPTOOL		      ?= /opt/Espressif/bin/esptool.py
endif


# Output directors to store intermediate compiled files
# relative to the project directory
BUILD_BASE   = build

# source code to compile
SRC_DIR	     = src

# path to libraries to compile from source
SRC_LIBDIR   = lib
SRC_LIBS     =

# SDK libraries to link
LIBS         = gcc hal pp phy net80211 lwip wpa main crypto freertos 
LIBS        += 

# compiler flags using during compilation of source files
CFLAGS      ?= -Os -Wpointer-arith -Wundef -fno-inline-functions -Werror
CFLAGS      += -Wl,-EL -nostdlib -mlongcalls -mtext-section-literals  -D__ets__ \
               -DICACHE_FLASH -ffunction-sections -fdata-sections -fno-builtin-printf \
               -fno-jump-tables --std=c99 \
               -fno-unwind-tables -fno-asynchronous-unwind-tables -fno-math-errno


# linker flags used to generate the main object file
LDFLAGS     += -Wl,--gc-sections -nostdlib -Wl,--no-check-sections -u call_user_start -Wl,-static -Wl,-O -Wl,-s

# FLASH size
FLASH_SIZE   = 1024

# various paths from the SDK used in this project
SDK_LIBDIR  = lib
SDK_LDDIR   = ld
SDK_INCDIR  = include include/json include/espressif extra_include include/lwip include/lwip/ipv4 include/lwip/ipv6

# select which tools to use as compiler, librarian and linker
CC := $(XTENSA_TOOLS_ROOT)/xtensa-lx106-elf-gcc
AR := $(XTENSA_TOOLS_ROOT)/xtensa-lx106-elf-ar
LD := $(XTENSA_TOOLS_ROOT)/xtensa-lx106-elf-gcc


####
#### no user configurable options below here
####

MAKEFILE_PATH := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BUILD_BASE  := $(addprefix $(MAKEFILE_PATH),$(BUILD_BASE))
BUILD_DIR   := $(addprefix $(BUILD_BASE)/,$(SRC_DIR))

SDK_LIBDIR  := $(addprefix $(SDK_PATH)/,$(SDK_LIBDIR))
SDK_INCDIR  := $(addprefix -I$(SDK_PATH)/,$(SDK_INCDIR))

SRC         := $(foreach sdir,$(SRC_DIR),$(wildcard $(sdir)/*.c))
OBJ         := $(patsubst %.c,$(BUILD_BASE)/%.o,$(SRC))
DEP         := $(patsubst %.c,$(BUILD_BASE)/%.d,$(SRC))
LIBS        := $(addprefix -l,$(LIBS))
APP_AR      := $(addprefix $(BUILD_BASE)/lib,user.a)

ifeq ($(FLASH_SIZE),512)
LD_SCRIPTS   := eagle.app.v6.ld
FW_OFFSET    := 0x41000
RFCAL_OFFSET := 0x7c000
endif

ifeq ($(FLASH_SIZE),1024)
LD_SCRIPTS   := eagle.app.v6.new.1024.app1.ld eagle.app.v6.new.1024.app2.ld
FW_OFFSET    := 0x81000
RFCAL_OFFSET := 0xfc000
endif

ifeq ($(FLASH_SIZE),2048)
LD_SCRIPTS   := eagle.app.v6.new.2048.ld
FW_OFFSET    := 0x101000
RFCAL_OFFSET := 0x1fc000
endif

ifeq ($(FLASH_SIZE),4096)
LD_SCRIPTS   := eagle.app.v6.new.2048.ld
FW_OFFSET    := 0x101000
RFCAL_OFFSET := 0x3fc000
endif


ifeq ($(LD_SCRIPTS),eagle.app.v6.ld)
TARGET1 := $(addprefix $(BUILD_BASE)/,user.elf)
else
	ifeq ($(LD_SCRIPTS),eagle.app.v6.new.2048.ld) 
        TARGET1 := $(addprefix $(BUILD_BASE)/,user.app1.elf)
    else
        TARGET1 := $(addprefix $(BUILD_BASE)/,user.app1.elf)
        TARGET2 := $(addprefix $(BUILD_BASE)/,user.app2.elf)
	endif
endif

#LD_SCRIPTS  := $(addprefix -T$(SDK_PATH)/$(SDK_LDDIR)/,$(LD_SCRIPTS))
INCDIR      := $(addprefix -I,$(SRC_DIR))

LIB_SRC_DIRS := $(addprefix $(SRC_LIBDIR)/,$(SRC_LIBS))
LIB_INC_DIRS := $(addsuffix /include,$(addprefix -I,$(LIB_SRC_DIRS)))
SRC_LD_LIBS  := -L$(BUILD_BASE)/$(SRC_LIBDIR) $(addprefix -l,$(SRC_LIBS))

# If we have a flash chip with 2 MegaBytes or more (16 MBit) we only generate
# one firmware image as both firmware partitions will be memory mapped to the
# complete address space. If we have less than that (ESP01 Modules) we
# generate two files with different load addresses
FW_FILE := $(addprefix firmware/,$(FW_FILE_ADDR).bin)

# if we're using the old non-bootloader script, we need to generate a v1 build
ifeq ($(LD_SCRIPTS),eagle.app.v6.ld)
    ELF2IMAGE_VERSION := 1
    ESPTOOL_EXT       := -
    WRITE_FLASH       := 0x00000 firmware/user-0x00000.bin 0x20000 firmware/user-0x20000.bin $(RFCAL_OFFSET) $(SDK_PATH)/bin/esp_init_data_default.bin
else
    ELF2IMAGE_VERSION := 2
    ESPTOOL_EXT       := .bin
	ifeq ($(LD_SCRIPTS),eagle.app.v6.new.2048.ld)
    	WRITE_FLASH       := 0x00000 $(SDK_PATH)/bin/boot_v1.7.bin 0x01000 firmware/user.app1.bin $(FW_OFFSET) firmware/user.app1.bin $(RFCAL_OFFSET) $(SDK_PATH)/bin/esp_init_data_default.bin
	else
    	WRITE_FLASH       := 0x00000 $(SDK_PATH)/bin/boot_v1.7.bin 0x01000 firmware/user.app1.bin $(FW_OFFSET) firmware/user.app2.bin $(RFCAL_OFFSET) $(SDK_PATH)/bin/esp_init_data_default.bin
    endif
endif

# Verbose mode
V ?= $(VERBOSE)
ifeq ("$(V)","1")
Q :=
vecho := @true
else
Q := @
vecho := @echo
endif

vpath %.c $(SRC_DIR)

define compile-objects
$1/%.o: %.c
	$(vecho) "CC $$<"
	$(Q) $(CC) $(INCDIR) $(LIB_INC_DIRS) $(SDK_INCDIR) $(CFLAGS) -c $$< -o $$@
endef

define make-depend
$1/%.d: %.c checkdirs
	$(vecho) "Depend $$<"
	$(Q) set -e; rm -f $$@; \
	 $(CC) -M $(INCDIR) $(LIB_INC_DIRS) $(SDK_INCDIR) $(CPPFLAGS) $$< > $$@.$$$$$$$$; \
	 sed 's,\(.*\)\.o[ :]*,$(BUILD_BASE)/$$(dir $$<)\1.o $$@: ,g' < $$@.$$$$$$$$ > $$@; \
	 rm -f $$@.$$$$$$$$
endef

.PHONY: all checkdirs flash clean libdirs $(LIB_SRC_DIRS)

all: checkdirs libdirs $(TARGET1) $(TARGET2)

libdirs: $(LIB_SRC_DIRS) 

$(LIB_SRC_DIRS):
	$(MAKE) -C $@ BUILD_DIR="$(BUILD_BASE)/$@"

$(TARGET1): $(APP_AR)
	$(vecho) "LD $@"
	$(Q) if [ $(FLASH_SIZE) -eq 512 ] ; then \
		echo "ATTENTION: This firmware will not be updateable over the air," ; \
		echo "           you'll need at least 1MB of flash memory for that." ; \
	fi
	$(Q) $(LD) -L$(SDK_LIBDIR) -T$(SDK_PATH)/$(SDK_LDDIR)/$(word 1, $(LD_SCRIPTS)) $(LDFLAGS) -Wl,--start-group $(LIBS) $(SRC_LD_LIBS) $< -Wl,--end-group -o $@
	$(Q) $(ESPTOOL) elf2image --version=$(ELF2IMAGE_VERSION) -o firmware/$(patsubst %.elf,%$(ESPTOOL_EXT),$(notdir $@)) $@

$(TARGET2): $(APP_AR)
	$(vecho) "LD $@"
	$(Q) $(LD) -L$(SDK_LIBDIR) -T$(SDK_PATH)/$(SDK_LDDIR)/$(word 2, $(LD_SCRIPTS)) $(LDFLAGS) -Wl,--start-group $(LIBS) $(SRC_LD_LIBS) $< -Wl,--end-group -o $@
	$(Q) $(ESPTOOL) elf2image --version=$(ELF2IMAGE_VERSION) -o firmware/$(patsubst %.elf,%$(ESPTOOL_EXT),$(notdir $@)) $@

$(APP_AR): $(OBJ)
	$(vecho) "AR $@"
	$(Q) $(AR) cru $@ $^

checkdirs: $(BUILD_DIR) firmware

$(BUILD_DIR):
	$(Q) mkdir -p $@

firmware:
	$(Q) mkdir -p $@

flash: $(TARGET1) $(TARGET2)
	$(ESPTOOL) --port $(SERIALPORT) write_flash $(WRITE_FLASH)

clean:
	$(Q) rm -rf firmware/ $(BUILD_BASE)

$(foreach bdir,$(BUILD_DIR),$(eval $(call compile-objects,$(bdir))))
$(foreach bdir,$(BUILD_DIR),$(eval $(call make-depend,$(bdir))))
include $(DEP)

export CFLAGS
export LDFLAGS

export XTENSA_TOOLS_ROOT
export SDK_PATH
export BUILD_BASE

export SDK_LIBDIR
export SDK_LDDIR
export SDK_INCDIR
export CC
export AR
export LD
