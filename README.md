# High-Speed Sensor Telemetry & Observer System Validation Board

[![Hardware: STM32F407VGT](https://img.shields.io/badge/Hardware-STM32F407VGT-blue.svg)](https://www.st.com/)
[![Firmware: C++](https://img.shields.io/badge/Firmware-C%2B%2B-orange.svg)](https://isocpp.org/)
[![Software: Python (PySide/PyQt)](https://img.shields.io/badge/GUI-Python-green.svg)](https://www.python.org/)
[![Data Rate: 200Hz](https://img.shields.io/badge/Data_Rate-200Hz-brightgreen.svg)]()

## Project Overview
This repository contains the full hardware, firmware, and software stack for a custom sensor data acquisition board designed around the STM32F407VGT microcontroller. The system is engineered to capture, process, and stream multi-sensor data to validate a high-speed observer system framework. 

The architecture bridges custom PCB design, non-blocking C++ embedded firmware, and a modular Python dashboard to provide real-time telemetry, enabling precise tracking of stable motor rotation and load variables at high velocities.

---

## System Architecture

### 1. Hardware Integration (`/hardware`)
The custom-designed PCB acts as the central node for sensor fusion and motor state estimation. The board integrates the following components:
*   **MCU:** STM32F407VGT (ARM Cortex-M4).
*   **IMU:** MPU6050 (6-axis accelerometer and gyroscope) for inertial tracking.
*   **Magnetometer:** HMC5883L for heading reference.
*   **Time-of-Flight:** VL53L0X for precise distance measurements.
*   **Mechanical Sensors:** Direct interfaces for load cells and quadrature/optical encoders to track torque and rotation.
*   **Design Files:** KiCAD schematics, BOM, and mechanical CAD models are included.

### 2. Embedded Firmware (`/firmware`)
Written in C++, the firmware focuses on deterministic execution and high-speed data throughput:
*   **Non-Blocking I/O:** Ensures the sensor polling loop is not bottlenecked by communication delays.
*   **Telemetry Pipeline:** Constructs and streams an 84-byte binary payload containing timestamped sensor data and state variables.
*   **Virtual COM Port (VCP):** Utilizes USB CDC to achieve a stable 200Hz data transmission rate to the host PC. 

### 3. Telemetry Dashboard (`/software`)
A custom graphical interface developed in Python (PySide/PyQt) to visualize the observer system's performance in real-time.
*   **Serial Parsing (`comms.py`):** Efficiently unpacks the 84-byte binary stream at 200Hz.
*   **Real-Time Visualization (`gauges.py` / `ui/`):** Dynamic plotting of motor rotation, current readings, IMU data, and load metrics.
*   **Architecture:** Highly modular layout utilizing custom `.qss` stylesheets for a clean, industrial UI.

---

##  Getting Started

### Prerequisites
*   **Hardware:** STM32 ST-LINK Utility or OpenOCD.
*   **Firmware:** ARM GCC Toolchain and CMake (or your preferred STM32 IDE like STM32CubeIDE).
*   **Software:** Python 3.8+ with `pyserial`, `PySide6` (or `PyQt6`), and `pyqtgraph`.

### Installation & Execution
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/yourusername/stm32-telemetry-board.git](https://github.com/yourusername/stm32-telemetry-board.git)
    cd stm32-telemetry-board
    ```
2.  **Flash the Firmware:** 
    Compile the C++ source in the `/firmware` directory and flash the STM32F407 via ST-LINK.
3.  **Launch the Dashboard:**
    ```bash
    cd software
    pip install -r requirements.txt
    python main.py
    ```

---

## 🔬 Current Development Status
*   [x] Custom PCB schematic and layout finalized.
*   [x] Virtual COM port pipeline validated (84-byte payload @ 200Hz).
*   [x] Python GUI rendering stable high-speed sensor plots.
*   [ ] Full observer system implementation in firmware (In Progress).

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
