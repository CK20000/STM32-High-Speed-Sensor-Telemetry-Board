# ui/tab_manager.py
from PySide6.QtWidgets import QStackedWidget
from core.comms import STM32DataBridge

from ui.tab0_home import Tab0_HOME
from ui.tab1_acc import Tab1_ACC
from ui.tab2_vlx import Tab2_VLX
from ui.tab3_enc import Tab3_ENC
from ui.tab4_ldc import Tab4_LDC
from ui.tab5_pot import Tab5_POT
from ui.tab6_mag import Tab6_MAG
from ui.tab7_err import Tab6_ERR

from ui.fast_plot_handler import FastPlotHandler

class TabManager(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.tab0 = Tab0_HOME()
        self.tab1 = Tab1_ACC()
        self.tab2 = Tab2_VLX()
        self.tab3 = Tab3_ENC()
        self.tab4 = Tab4_LDC()
        self.tab5 = Tab5_POT()
        self.tab6 = Tab6_MAG()
        self.tab7 = Tab6_ERR()

        self.addWidget(self.tab0)
        self.addWidget(self.tab1)
        self.addWidget(self.tab2)
        self.addWidget(self.tab3)
        self.addWidget(self.tab4)
        self.addWidget(self.tab5)
        self.addWidget(self.tab6)
        self.addWidget(self.tab7)

        # --- INITIALIZE THE HIGH SPEED BRIDGE ---
        self.bridge = STM32DataBridge(baudrate=500000)
        self.bridge.start()

        # --- INJECT THE RENDERING ENGINE ---
        self.plot_handler = FastPlotHandler(self, self.bridge)

        self.setup_cross_tab_wiring()

    def update_connection_ui(self, message, is_connected):
        """Merges connection status directly into the Master Toggle Button's Neon styling"""
        btn = self.tab0.btn_master

        # We inject the QSS directly.
        # Unchecked = Glowing Border. Checked = Solid Filled Background.
        if is_connected:
            btn.setText("MASTER ON")
            # --- GREEN/CYAN NEON (Connected) ---
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a24;
                    color: #00ffcc;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #00ffcc;
                    border-radius: 4px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 204, 0.1);
                }
                QPushButton:checked {
                    background-color: rgba(0, 255, 204, 0.25);
                    color: #ffffff;
                    border: 2px solid #00ffcc;
                }
            """)
        else:
            btn.setText("MASTER ON")
            # --- YELLOW/ORANGE NEON (Searching) ---
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a24;
                    color: #ffaa00;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #ffaa00;
                    border-radius: 4px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 170, 0, 0.1);
                }
                QPushButton:checked {
                    background-color: rgba(255, 170, 0, 0.25);
                    color: #ffffff;
                    border: 2px solid #ffaa00;
                }
            """)

    def setup_cross_tab_wiring(self):
        """Central Switchboard for GUI logic and TX Transmission"""
        home = self.tab0

        # 1. UI WIRING: Tie toggles to the Home Tab Red Blocks
        self.tab1.btn_enable.toggled.connect(lambda state: home.trigger_sensor("MPU6050 1", state))
        self.tab1.btn_enable.toggled.connect(lambda state: home.trigger_sensor("MPU6050 2", state))
        self.tab1.btn_heater_enable.toggled.connect(lambda state: home.trigger_sensor("HEATER", state))

        self.tab2.btn_enable.toggled.connect(lambda state: home.trigger_sensor("VL53L0X", state))
        self.tab3.btn_enable.toggled.connect(lambda state: home.trigger_sensor("OPTICAL ENC", state))
        self.tab3.btn_enable.toggled.connect(lambda state: home.trigger_sensor("MAG ENC", state))
        self.tab4.btn_enable.toggled.connect(lambda state: home.trigger_sensor("LOAD CELL", state))
        self.tab4.btn_enable.toggled.connect(lambda state: home.trigger_sensor("BMP280", state))
        self.tab5.btn_enable.toggled.connect(lambda state: home.trigger_sensor("POT 1", state))
        self.tab5.btn_enable.toggled.connect(lambda state: home.trigger_sensor("POT 2", state))
        self.tab5.btn_enable.toggled.connect(lambda state: home.trigger_sensor("POT 3", state))
        self.tab6.btn_enable.toggled.connect(lambda state: home.trigger_sensor("MAGNETOMETER", state))

        # 2. TX WIRING: Whenever ANY toggle is clicked, recalculate and send the bitmask to STM32
        all_toggles = [
            self.tab0.btn_master, self.tab1.btn_enable, self.tab2.btn_enable,
            self.tab3.btn_enable, self.tab4.btn_enable, self.tab5.btn_enable, self.tab6.btn_enable
        ]
        for btn in all_toggles:
            btn.toggled.connect(self.transmit_state_to_stm32)

        # --- CONNECT THE NEW SMART-STATUS SIGNAL ---
        self.bridge.connection_status.connect(self.update_connection_ui)
        self.bridge.sys_data.connect(self.update_home_gauges)

    def transmit_state_to_stm32(self):
        """Calculates the active bits and fires them via serial"""
        mask = 0
        if self.tab1.btn_enable.isChecked(): mask |= (1 << 0)  # Bit 0: Accels
        if self.tab2.btn_enable.isChecked(): mask |= (1 << 1)  # Bit 1: VLX
        if self.tab3.btn_enable.isChecked(): mask |= (1 << 2)  # Bit 2: Encoders
        if self.tab4.btn_enable.isChecked(): mask |= (1 << 3)  # Bit 3: Load/Press
        if self.tab5.btn_enable.isChecked(): mask |= (1 << 4)  # Bit 4: Pots
        if self.tab6.btn_enable.isChecked(): mask |= (1 << 5)  # Bit 5: Mag

        master_on = self.tab0.btn_master.isChecked()

        # Send it!
        self.bridge.send_gui_state(master_on, mask)

    def update_home_gauges(self, latency, cpu):
        """Live updates the GX Arc Gauges from the STM32 thread"""
        self.tab0.gauge_loop.update_value(latency)
        self.tab0.gauge_mem.update_value(cpu)

    def stop_bridge(self):
        self.bridge.stop()
