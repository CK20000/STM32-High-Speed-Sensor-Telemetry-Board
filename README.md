# STM32 High-Speed Sensor Telemetry Board

## Overview
This repository contains the hardware design, embedded C++ firmware, and Python dashboard for a custom sensor data acquisition board. Designed around the STM32F407VGT, the system reads multiple sensors and streams an 84-byte telemetry packet via a Virtual COM port at 200Hz.

## Features
*   **Hardware:** Integrates MPU6050, HMC5883L, VL53L0X, load cells, and encoders.
*   **Firmware:** Non-blocking C++ implementation ensuring stable motor rotation and high-speed telemetry.
*   **Software:** Modular Python dashboard with real-time data plotting and serial parsing.
