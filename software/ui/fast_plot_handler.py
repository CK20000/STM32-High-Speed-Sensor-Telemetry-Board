import numpy as np
from PySide6.QtCore import QTimer


# --- THE HIGH-PERFORMANCE RENDERING ENGINE ---
class FastPlotHandler:
    def __init__(self, tab_manager, bridge):
        self.tabs = tab_manager
        self.bridge = bridge
        self.points = 500  # How many data points wide the screen is

        # 1. Pre-allocate Blazing Fast Numpy Buffers
        self.acc1_x = np.zeros(self.points);
        self.acc1_y = np.zeros(self.points);
        self.acc1_z = np.zeros(self.points)
        self.acc2_x = np.zeros(self.points);
        self.acc2_y = np.zeros(self.points);
        self.acc2_z = np.zeros(self.points)
        self.vlx_dist = np.zeros(self.points)
        self.ldc_w = np.zeros(self.points);
        self.bmp_p = np.zeros(self.points)
        self.mag_x = np.zeros(self.points);
        self.mag_y = np.zeros(self.points);
        self.mag_z = np.zeros(self.points)

        # Instantaneous values for gauges (no history needed)
        self.opt_val = 0;
        self.mag_val = 0
        self.pot1 = 0;
        self.pot2 = 0
        self.pot3 = 0

        # 2. Wire High-Speed Comm Signals directly into the Buffers (NOT to the UI)
        self.bridge.acc1_data.connect(self.buf_acc1)
        self.bridge.acc2_data.connect(self.buf_acc2)
        self.bridge.vlx_data.connect(self.buf_vlx)
        self.bridge.ldc_press_data.connect(self.buf_ldc_press)
        self.bridge.mag_data.connect(self.buf_mag)
        self.bridge.enc_data.connect(self.buf_enc)
        self.bridge.pot_data.connect(self.buf_pots)

        # 3. The 30FPS UI Framerate Lock
        self.timer = QTimer()
        self.timer.timeout.connect(self.paint_visible_tab_only)
        self.timer.start(33)  # 33ms = ~30 Frames Per Second

    # --- BUFFER SHIFTING LOGIC (Takes Microseconds) ---
    def buf_acc1(self, x, y, z):
        self.acc1_x[:-1] = self.acc1_x[1:];
        self.acc1_x[-1] = x
        self.acc1_y[:-1] = self.acc1_y[1:];
        self.acc1_y[-1] = y
        self.acc1_z[:-1] = self.acc1_z[1:];
        self.acc1_z[-1] = z

    def buf_acc2(self, x, y, z):
        self.acc2_x[:-1] = self.acc2_x[1:];
        self.acc2_x[-1] = x
        self.acc2_y[:-1] = self.acc2_y[1:];
        self.acc2_y[-1] = y
        self.acc2_z[:-1] = self.acc2_z[1:];
        self.acc2_z[-1] = z

    def buf_vlx(self, dist):
        self.vlx_dist[:-1] = self.vlx_dist[1:];
        self.vlx_dist[-1] = dist

    def buf_ldc_press(self, w, p):
        self.ldc_w[:-1] = self.ldc_w[1:];
        self.ldc_w[-1] = w
        self.bmp_p[:-1] = self.bmp_p[1:];
        self.bmp_p[-1] = p

    def buf_mag(self, x, y, z):
        self.mag_x[:-1] = self.mag_x[1:];
        self.mag_x[-1] = x
        self.mag_y[:-1] = self.mag_y[1:];
        self.mag_y[-1] = y
        self.mag_z[:-1] = self.mag_z[1:];
        self.mag_z[-1] = z

    def buf_enc(self, opt, mag):
        self.opt_val = opt;
        self.mag_val = mag

    def buf_pots(self, p1, p2, p3):
        self.pot1 = p1;
        self.pot2 = p2
        self.pot3 = p3

    # --- THE SMART RENDERER ---
    def paint_visible_tab_only(self):
        """Only spends GPU cycles rendering the tab you are actively looking at"""
        current_tab = self.tabs.currentIndex()

        if current_tab == 1:  # ACC
            if self.tabs.tab1.btn_enable.isChecked():
                # Feed data to Plot 1 (MPU6050 0x68)
                self.tabs.tab1.line1_x.setData(self.acc1_x)
                self.tabs.tab1.line1_y.setData(self.acc1_y)
                self.tabs.tab1.line1_z.setData(self.acc1_z)

                # Feed data to Plot 2 (MPU6050 0x69)
                self.tabs.tab1.line2_x.setData(self.acc2_x)
                self.tabs.tab1.line2_y.setData(self.acc2_y)
                self.tabs.tab1.line2_z.setData(self.acc2_z)

        elif current_tab == 2:  # VLX
            if self.tabs.tab2.btn_enable.isChecked():
                self.tabs.tab2.line_dist.setData(self.vlx_dist)

        elif current_tab == 3:  # ENC (Dials)
            if self.tabs.tab3.btn_enable.isChecked():
                # Dials don't take arrays, they just take the instantaneous value
                self.tabs.tab3.dial_optical.update_values(self.opt_val)
                self.tabs.tab3.dial_magnetic.update_values(self.mag_val)
                self.tabs.tab3.dial_combined.update_values(self.opt_val, self.mag_val)

        elif current_tab == 4:  # LDC / PRESS
            if self.tabs.tab4.btn_enable.isChecked():
                self.tabs.tab4.line_weight.setData(self.ldc_w)
                self.tabs.tab4.line_press.setData(self.bmp_p)


        elif current_tab == 5:  # POTS (Arc Gauges)

            if self.tabs.tab5.btn_enable.isChecked():
                self.tabs.tab5.pot1_dial.update_value(self.pot1)
                self.tabs.tab5.pot2_dial.update_value(self.pot2)
                self.tabs.tab5.pot3_dial.update_value(self.pot3)  # <--- ADD THIS


        elif current_tab == 6:  # MAG

            if self.tabs.tab6.btn_enable.isChecked():
                self.tabs.tab6.line_x.setData(self.mag_x)
                self.tabs.tab6.line_y.setData(self.mag_y)
                self.tabs.tab6.line_z.setData(self.mag_z)

            # Run the ESC Safety logic regardless of whether the MAG plot stream is toggled!
            self.tabs.tab6.update_esc_safety(self.pot1)
