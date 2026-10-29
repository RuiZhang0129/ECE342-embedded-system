/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
#include "main.h"

#include "config.h"
#include "ov7670.h"

#include <stdio.h>
#include <string.h>



uint16_t snapshot_buff[IMG_ROWS * IMG_COLS];

uint8_t dma_flag = 0;	// interupt


void print_test(void);
void print_grey_scale_image(void);

int main(void)
{
  /* Reset of all peripherals */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_DCMI_Init();
  MX_USART3_UART_Init();
  MX_USB_OTG_FS_PCD_Init();
  MX_I2C2_Init();
  MX_TIM1_Init();
  MX_TIM6_Init();

  char msg[100];

  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
  ov7670_init();
	HAL_Delay(100); 
	ov7670_capture(snapshot_buff);

  // Your start up code here
	print_msg("hello");

  while (1)
  {
    // Your code here
		
		// Starter code
		/*
    if (HAL_GPIO_ReadPin(USER_Btn_GPIO_Port, USER_Btn_Pin)) {
      dma_flag = 1;
			HAL_Delay(100);  // debounce
	
      // print_msg("Snap!\r\n");
    }
		*/
		
		//print_test();
		
		// part 3.5
		/*
		if (dma_flag == 1){
			HAL_DCMI_Stop(&hdcmi);
			print_msg("Snap!\r\n");
			ov7670_snapshot(snapshot_buff);
			print_grey_scale_image();
			dma_flag = 0;
			HAL_Delay(10000);
		}
		*/
		
		// part 4.2
		ov7670_capture(snapshot_buff);
		HAL_DCMI_Stop(&hdcmi);
		print_grey_scale_image();
		
		HAL_Delay(50);
		
  }
}

// part 2.1
void print_test(){
	for (int i = 0; i < (IMG_ROWS*IMG_COLS); i++){
			snapshot_buff[i] = 0xFF;
		}
		print_msg("\r\nPREAMBLE!\r\n");
		HAL_Delay(1000);
		uart_send_bin(snapshot_buff, 25056);
}

void print_grey_scale_image(){
	print_msg("PREAMBLE!\r\n");
	uint8_t* pxl = (uint8_t*)snapshot_buff;
	for(int i = 0; i <(IMG_ROWS*IMG_COLS); i++) {
		uart_send_bin(pxl+(2*i+1), 1);
	}
}