from PyQt5.QtWidgets import *
import time

import pyqtgraph as pg
from collections import deque

""" Here and advancedMtaps is where each mode tab is designed and defines user input parameter options.
Copy and paste one of these classes and change the name, then add what user parameters options are needed to 
suit user design, for example copy and paste the calibration class, then chnage the class name. go back the simple GUI script and
and register your new class"""

#  Calibration tab
class Calibration(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.motor = motor

        self.last_plot_time = 0

        layout = QVBoxLayout(self)

        # layer for start/stop buttons
        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(start_callback)

        self.btnStop = QPushButton("Stop")
        self.btnStop.clicked.connect(self.motor.stop_motor)

        top_layout.addWidget(self.btnStart)
        top_layout.addWidget(self.btnStop)

        layout.addLayout(top_layout)

        # Sensor input 
        sensor_layout = QHBoxLayout()

        self.sensor_input = QLineEdit()
        self.sensor_input.setPlaceholderText("Sensor Pin")

        
        sensor_layout.addWidget(QLabel("Sensor Pin:"))
        sensor_layout.addWidget(self.sensor_input)
    

        layout.addLayout(sensor_layout)

        # Speed input 
        speed_layout = QHBoxLayout()

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Speed")

   
         
        self.dropDownSpeed = QComboBox()
        self.dropDownSpeed.addItems(['Cycle/s', 'Rotations/s'])

        self.dropDownSpeed.activated.connect(self.activated)

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.dropDownSpeed)

        layout.addLayout(speed_layout)

        # Graph plotting parameters
        self.plot_graph = pg.PlotWidget()
        layout.addWidget(self.plot_graph)

        self.setup_plot()

        # Incoming data sorting for graph 
        self.start_time = time.time()

        self.time_data = deque(maxlen=30)
        self.value_A = deque(maxlen=30)
        self.value_B = deque(maxlen=30)

        for i in range(30):
            self.time_data.append(i)
            self.value_A.append(0)
            self.value_B.append(0)

        # Live graph plotting 
        self.line_A = self.plot_graph.plot(
            self.time_data, self.value_A, name="value_A", pen="r"
        )

        self.line_B = self.plot_graph.plot(
            self.time_data, self.value_B, name="value_B", pen="b"
        )

    def setup_plot(self):
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle("Motor Output vs Time", color="b", size="20pt")

        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Value", **styles)
        self.plot_graph.setLabel("bottom", "Time (s)", **styles)

        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        self.plot_graph.setYRange(0, 65535)  # adjust if needed

    #  this is needed to retrive the correct data
    def register_stream(self, cs_pin, router):
        self.cs_pin = cs_pin

        router.register(
            cs_pin,
            0x01,   # calibration mode
            self.receive_data
        )


    def receive_data(self, values):
        value_A, value_B = values

        t = time.time() - self.start_time

        self.time_data.append(t)
        self.value_A.append(value_A)
        self.value_B.append(value_B)

        # Limit redraw to ~20Hz
        if time.time() - self.last_plot_time > 0.05:
            self.line_A.setData(self.time_data, self.value_A)
            self.line_B.setData(self.time_data, self.value_B)
            self.last_plot_time = time.time()


    def activated(self, index):
        self.motor.set_speed_unit(index)
        print("Activated index:", index)

    def push_settings(self):
        self.motor.set_speed_from_text(self.speed_input.text())
        self.motor.set_sensor(self.sensor_input.text())

# INDEX POSITION tab

class IndexPosition(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.motor = motor

        layout = QVBoxLayout(self)

          # layer for start/stop buttons
        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(start_callback)

        self.btnStop = QPushButton("Stop")
        self.btnStop.clicked.connect(self.motor.stop_motor)

        top_layout.addWidget(self.btnStart)
        top_layout.addWidget(self.btnStop)

        layout.addLayout(top_layout)

          # Sensor input
        sensor_layout = QHBoxLayout()

        self.sensor_input = QLineEdit()
        self.sensor_input.setPlaceholderText("Sensor Pin")


        sensor_layout.addWidget(QLabel("Sensor Pin:"))
        sensor_layout.addWidget(self.sensor_input)
       

        layout.addLayout(sensor_layout)

         # Speed input 
        speed_layout = QHBoxLayout()

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Speed")

      
        speed_layout.addWidget(self.speed_input)
        

        self.dropDownSpeed = QComboBox()
        self.dropDownSpeed.addItems(['Cycle/s', 'Rotations/s'])

        self.dropDownSpeed.activated.connect(self.activated)

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.dropDownSpeed)

        layout.addLayout(speed_layout)

        home_layout = QHBoxLayout()

        self.btnhome = QPushButton("Home")
        self.btnhome.clicked.connect(self.motor.return_home)

        home_layout.addWidget(self.btnhome)

        layout.addLayout(home_layout)

    def activated(self, index):
        self.motor.set_speed_unit(index)
        print("Activated index:", index)

    def push_settings(self):
        self.motor.set_speed_from_text(self.speed_input.text())
        self.motor.set_sensor(self.sensor_input.text())


# BASIC ROTATION tap
class BasicRotationWidget(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.motor = motor

        layout = QVBoxLayout(self)

        # layer for start/stop buttons
        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(start_callback)

        self.btnStop = QPushButton("Stop")
        self.btnStop.clicked.connect(self.motor.stop_motor)

        top_layout.addWidget(self.btnStart)
        top_layout.addWidget(self.btnStop)

        layout.addLayout(top_layout)

        # Speed input 
        speed_layout = QHBoxLayout()

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Speed")


        speed_layout.addWidget(self.speed_input)
        


        self.dropDownSpeed = QComboBox()
        self.dropDownSpeed.addItems(['Cycle/s', 'Rotations/s'])

        self.dropDownSpeed.activated.connect(self.activated)

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.dropDownSpeed)

        layout.addLayout(speed_layout)

     

        # layout.addLayout(speed_layout)
    def activated(self, index):
        self.motor.set_speed_unit(index)
        print("Activated index:", index)


    def push_settings(self):
        self.motor.set_speed_from_text(self.speed_input.text())



# SYRINGE PUMP tab
class SyringePump(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.motor = motor

        layout = QVBoxLayout(self)

        # layer for start/stop buttons
        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(start_callback)

        self.btnStop = QPushButton("Stop")
        self.btnStop.clicked.connect(self.motor.stop_motor)

        top_layout.addWidget(self.btnStart)
        top_layout.addWidget(self.btnStop)

        layout.addLayout(top_layout)

        # Syringe Pump Parameeters 
        self.diameter_input = QLineEdit()
        self.diameter_input.setPlaceholderText("Diameter (mm)")
        self.diameter_input.textChanged.connect(self.push_settings)

        self.lead_input = QLineEdit()
        self.lead_input.setPlaceholderText("Lead (mm/rev)")
        self.lead_input.textChanged.connect(self.push_settings)

        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("Target Volume (mL)")
        self.volume_input.textChanged.connect(self.push_settings)

        self.flow_input = QLineEdit()
        self.flow_input.setPlaceholderText("Flow Rate (mL/s)")
        self.flow_input.textChanged.connect(self.push_settings)

        layout.addWidget(self.diameter_input)
        layout.addWidget(self.lead_input)
        layout.addWidget(self.volume_input)
        layout.addWidget(self.flow_input)

    def push_settings(self):
        self.motor.set_syringe_params(
            self.diameter_input.text(),
            self.lead_input.text(),
            self.volume_input.text(),
            self.flow_input.text()
        )