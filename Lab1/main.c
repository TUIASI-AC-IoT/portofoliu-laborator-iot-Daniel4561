#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define GPIO_OUTPUT_IO 4
#define GPIO_OUTPUT_PIN_SEL (1ULL<<GPIO_OUTPUT_IO)
#define GPIO_INPUT_IO 2
#define GPIO_INPUT_PIN_SEL (1ULL<<GPIO_INPUT_IO)

int cnt = 0;

static void count_button_press(void *arg)
{
    while(1)
    {
        if(gpio_get_level(GPIO_INPUT_IO) == 0)
            cnt += 1;
        vTaskDelay(50);
    }
    
}

void app_main() {
    //zero-initialize the config structure.
    gpio_config_t io_conf = {};
    //disable interrupt
    io_conf.intr_type = GPIO_INTR_DISABLE;
    //set as output mode
    io_conf.mode = GPIO_MODE_OUTPUT;
    //bit mask of the pins that you want to set
    io_conf.pin_bit_mask = GPIO_OUTPUT_PIN_SEL;
    //disable pull-down mode
    io_conf.pull_down_en = 0;
    //disable pull-up mode
    io_conf.pull_up_en = 0;
    //configure GPIO with the given settings
    gpio_config(&io_conf);

    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = GPIO_INPUT_PIN_SEL;
    io_conf.pull_up_en = 1;
    gpio_config(&io_conf);
	
	//int times[] = {1000, 500, 250, 750};
	
    xTaskCreate(count_button_press, "count_button_press", 2048, NULL, 10, NULL);

    while(1) {
        printf("cnt: %d\n", cnt);
        gpio_set_level(GPIO_OUTPUT_IO, cnt % 2);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}