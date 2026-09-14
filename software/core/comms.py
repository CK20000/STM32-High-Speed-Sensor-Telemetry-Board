# core/comms.py
import serial
import serial.tools.list_ports  # <--- CRITICAL FOR SMART DETECTION
import struct
import time
from PySide6.QtCore import QThread, Signal


class STM32DataBridge(QThread):
    # --- ADDED A NEW CONNECTION STATUS SIGNAL ---
    connection_status = Signal(str, bool)  # e.g. ("COM5", True) or ("SEARCHING...", False)

    sys_data = Signal(float, float)
    acc1_data = Signal(float, float, float)
    acc2_data = Signal(float, float, float)
    vlx_data = Signal(float)
    enc_data = Signal(float, float)
    ldc_press_data = Signal(float, float)
    pot_data = Signal(int, int, int)
    mag_data = Signal(float, float, float)

    def __init__(self, baudrate=500000):  # Notice: Removed the hardcoded 'port' arg!
        super().__init__()
        self.baudrate = baudrate
        self.is_running = False
        self.serial_conn = None

        self.packet_format = '<4s ff HH fff fff f ff ff iii fff'
        self.packet_size = struct.calcsize(self.packet_format)

    def find_stm32_port(self):
        """Scans the hardware registry for STM32 devices without opening ports"""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            # 0x0483 is STMicroelectronics. 0x5740 is their standard Virtual COM Port PID.
            if p.vid == 0x0483:
                return p.device
            # Fallback: Check if the device description explicitly says "STM32"
            if "STM" in (p.description or ""):
                return p.device
        return None

    def run(self):
        self.is_running = True
        sync_pattern = b'\xAA\xBB\xCC\xDD'
        buffer = b''

        while self.is_running:
            # ==========================================
            # STATE 1: SMART AUTO-CONNECT (0% CPU LOAD)
            # ==========================================
            if self.serial_conn is None or not self.serial_conn.is_open:
                self.connection_status.emit("SEARCHING FOR STM32...", False)

                port_name = self.find_stm32_port()

                if port_name:
                    try:
                        self.serial_conn = serial.Serial(port_name, self.baudrate, timeout=0)
                        self.connection_status.emit(f"STM32 CONNECTED // {port_name}", True)
                        buffer = b''  # Clear any old garbage data
                    except Exception as e:
                        time.sleep(1)  # Port found but locked by Windows, wait and retry
                        continue
                else:
                    time.sleep(1)  # SLEEP FOR 1 SECOND. Do not flood the CPU!
                    continue

            # ==========================================
            # STATE 2: HIGH-SPEED TELEMETRY LOOP
            # ==========================================
            try:
                if self.serial_conn.in_waiting > 0:
                    buffer += self.serial_conn.read(self.serial_conn.in_waiting)

                    while True:
                        sync_idx = buffer.find(sync_pattern)

                        if sync_idx == -1:
                            buffer = buffer[-3:] if len(buffer) >= 3 else buffer
                            break

                        if sync_idx > 0:
                            buffer = buffer[sync_idx:]

                        if len(buffer) < self.packet_size:
                            break

                        frame = buffer[:self.packet_size]
                        buffer = buffer[self.packet_size:]

                        parsed = struct.unpack(self.packet_format, frame)

                        self.sys_data.emit(parsed[1], parsed[2])
                        self.acc1_data.emit(parsed[5], parsed[6], parsed[7])
                        self.acc2_data.emit(parsed[8], parsed[9], parsed[10])
                        self.vlx_data.emit(parsed[11])
                        self.enc_data.emit(parsed[12], parsed[13])
                        self.ldc_press_data.emit(parsed[14], parsed[15])
                        self.pot_data.emit(parsed[16], parsed[17], parsed[18])
                        self.mag_data.emit(parsed[19], parsed[20], parsed[21])
                else:
                    time.sleep(0.005) # <--- CHANGE THIS FROM 0.001 TO 0.005

            except serial.SerialException:
                # CABLE UNPLUGGED! Catch the crash safely and return to STATE 1
                self.serial_conn.close()
                self.serial_conn = None

    def send_gui_state(self, master_on, active_mask):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                cmd = struct.pack('<BBBB', 0xAA, 0xBB, int(master_on), active_mask)
                self.serial_conn.write(cmd)
            except serial.SerialException:
                pass  # Ignore write errors if cable is yanked mid-click

    def stop(self):
        self.is_running = False
        self.wait()