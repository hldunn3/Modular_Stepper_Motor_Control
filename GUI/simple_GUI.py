import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import basicMtaps as BMT
import advancedMtaps as AMT
import packet_creation
from serial_router import SerialRouter
import pyqtgraph as pg
import psutil
import os

"""
Main Motor function window, within this window the important parameters 
are selected which applies to all modes within the tap modes
"""

class MotorWidget(QGroupBox):

    def __init__(self, motor_number, router):
        super().__init__(f"Motor {motor_number}")

        self.router = router
        self.motor = packet_creation.Packet_Creation()

        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        # Defining the input for the CS pin 

        self.cs_input = QLineEdit()
        self.cs_input.setPlaceholderText("CS Pin")

        self.btnSetCS = QPushButton("Set CS")
        self.btnSetCS.clicked.connect(self.set_cs_and_register)

        top_layout.addWidget(QLabel("CS Pin:"))
        top_layout.addWidget(self.cs_input)
        top_layout.addWidget(self.btnSetCS)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)   


        # Define the layer for the Reverse and Disable button 
        second_layout = QHBoxLayout()

        self.reverse_checkbox = QCheckBox("Reverse")
        self.reverse_checkbox.stateChanged.connect(self.motor.reverse_motor)
        second_layout.addWidget(self.reverse_checkbox)   

        self.disable_checkbox = QCheckBox("Disable")
        self.disable_checkbox.stateChanged.connect(self.motor.disable_motor)
        second_layout.addWidget(self.disable_checkbox)

        main_layout.addLayout(second_layout)   

        # Define the tab bar where all tab modes are found and selected, also this 
        # is where more tabs (modes) can be registered with the motor mode window.   

        self.tabs = QTabWidget()

        self.calibration = BMT.Calibration(self.motor, self.start_with_settings)
        self.tabs.addTab(self.calibration, "Motor Calibration")

        self.index_position = BMT.IndexPosition(self.motor, self.start_with_settings)
        self.tabs.addTab(self.index_position, "Index Position")

        self.basic_tab = BMT.BasicRotationWidget(self.motor, self.start_with_settings)
        self.tabs.addTab(self.basic_tab, "Basic Rotation")

        self.syringe_tab = BMT.SyringePump(self.motor, self.start_with_settings)
        self.tabs.addTab(self.syringe_tab, "Syringe Pump")

        self.valve = AMT.Valve(self.motor, self.start_with_settings)
        self.tabs.addTab(self.valve, "Valve Control")

        self.peristaltic = AMT.Peristaltic(self.motor, self.start_with_settings)
        self.tabs.addTab(self.peristaltic, "Peristaltic Pump")

        # Here you would add a new tab,but first a new class needs to be created, examples are 
        # located within the basicMtaps or advancedMtaps. or creat a new script containing a 
        # motor mode class. Once this is done just call on the class like the examples above. 

        main_layout.addWidget(self.tabs)

        self.tabs.currentChanged.connect(self.on_tab_changed)

    # this defintion is related to routing data coming from the teensy to the correct motor and mode
    # tabe. 
    def set_cs_and_register(self):
        cs_text = self.cs_input.text()
        self.motor.set_cs_pin(cs_text)

        try:
            cs = int(cs_text)
        except:
            return

        # to register a new mode for data routing, just register like the examples below
        self.calibration.register_stream(cs, self.router)
        self.valve.register_stream(cs, self.router)
        self.peristaltic.register_stream(cs, self.router)

    # when mode is changed the number is sent to packet creation in readniess to send 
    # command packet, A new mode will need to be conjiguered here aswell 

    def on_tab_changed(self, index):

        if index == 0:
            self.motor.set_mode(0x01)
            self.calibration.push_settings()

        elif index == 1:
            self.motor.set_mode(0x02)
            self.index_position.push_settings()

        elif index == 2:
            self.motor.set_mode(0x03)
            self.basic_tab.push_settings()

        elif index == 3:
            self.motor.set_mode(0x04)
            self.syringe_tab.push_settings()

        elif index == 4:
            self.motor.set_mode(0x05)
            self.valve.push_settings()

        elif index == 5:
            self.motor.set_mode(0x06)
            self.peristaltic.push_settings()
            
    def start_with_settings(self):
        current_widget = self.tabs.currentWidget()

        if hasattr(current_widget, "push_settings"):
            current_widget.push_settings()

        self.motor.start_motor()


"""
Main GUI window
"""

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stepper Motor Setup")
        self.resize(1200, 1000)

        
        # the commented section is within SerialRouter is the teensy id essentially,
        # different for every teensy or microcontroller 

        # PCB teensy 
        self.router = SerialRouter(
            '/dev/serial/by-id/usb-Teensyduino_USB_Serial_18671260-if00'
        )

        # Circuit board teensy 
        # self.router = SerialRouter(
        #     '/dev/serial/by-id/usb-Teensyduino_USB_Serial_18660570-if00'
        # )


        main_layout = QVBoxLayout()

        perf_layout = QHBoxLayout()

        self.process = psutil.Process(os.getpid())

        self.ram_label = QLabel("RAM: 0 MB")
        self.cpu_label = QLabel("CPU: 0 %")

        perf_layout.addWidget(self.ram_label)
        perf_layout.addWidget(self.cpu_label)
        perf_layout.addStretch()

        main_layout.addLayout(perf_layout)

        # Add / Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+ Add Motor")
        self.remove_button = QPushButton("- Remove Motor")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        main_layout.addLayout(button_layout)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.motor_container = QWidget()

        self.motor_layout = QGridLayout(self.motor_container)
        self.motor_layout.setSpacing(15)
        self.motor_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll.setWidget(self.motor_container)
        main_layout.addWidget(self.scroll)

        self.setLayout(main_layout)

        self.motor_count = 0
        self.motor_widgets = []

        self.add_button.clicked.connect(self.add_motor)
        self.remove_button.clicked.connect(self.remove_motor)

        # Timer for when CPU and RAM are updated on GUI screen 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_performance)
        self.timer.start(1000)

    # retriving the CPU and RAM vlaues from the raspberry PI 
    def update_performance(self):
        ram = self.process.memory_info().rss / (1024**2)
        cpu = self.process.cpu_percent(interval=None)

        self.ram_label.setText(f"RAM: {ram:.2f} MB")
        self.cpu_label.setText(f"CPU: {cpu:.1f} %")

    def add_motor(self):
        self.motor_count += 1

        motor = MotorWidget(self.motor_count, self.router)
        motor.setFixedSize(550, 600)

        self.motor_widgets.append(motor)

        index = len(self.motor_widgets) - 1
        row = index // 2
        col = index % 2

        self.motor_layout.addWidget(motor, row, col)

    def remove_motor(self):
        if self.motor_widgets:
            motor = self.motor_widgets.pop()
            self.motor_layout.removeWidget(motor)
            motor.setParent(None)
            self.motor_count -= 1


if __name__ == "__main__":
    pg.setConfigOptions(antialias=False)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())