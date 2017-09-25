/*
 * Copyright 2017 Johannes Schriewer <hallo@dunkelstern.de>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <esp_common.h>

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include <c_types.h>
#include <spi_flash.h>

// This is called by the SDK to fetch the SDK settings sector,
// we use the default and give it the last five sectors of flash
uint32 user_rf_cal_sector_set(void) {
    extern char flashchip;
    SpiFlashChip *flash = (SpiFlashChip*)(&flashchip + 4);
    // We know that sector size in 4096
    //uint32_t sec_num = flash->chip_size / flash->sector_size;
    uint32_t sec_num = flash->chip_size >> 12;
    return sec_num - 5;
}

// Wifi event handler, will be called if we got an IP address in Station mode
void ICACHE_FLASH_ATTR wifi_event_handler_cb(System_Event_t *event) {
    static int running = 0;

    if (event->event_id == EVENT_STAMODE_GOT_IP) {
        // We have an IP address
        // TODO: run all services that need this address now
    }
}

// Entry point that will be called from the SDK, setup everything here...
void user_init(void) {
    printf("SDK version: %s\n", system_get_sdk_version());
    wifi_set_event_handler_cb(wifi_event_handler_cb);

    // TODO: Initialization tasks, probably run a few RTOS tasks?
}