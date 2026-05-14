from PyQt5.QtWidgets import *
import time

import pyqtgraph as pg
from collections import deque
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *
import time
import pyqtgraph as pg
from collections import deque
from PyQt5.QtCore import Qt
import csv
import os


class Valve(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.target_value = 0
        self.value_target = deque(maxlen=30)
        self.csv_saved = False

        self.record_time = []
        self.record_A = []
        self.record_B = []

        for _ in range(30):
            self.value_target.append(0)

        self.motor = motor
        self.start_callback = start_callback
        self.last_plot_time = 0

        layout = QVBoxLayout(self)

         # layer for start/stop buttons
        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.start_pressed)  # ✅ CHANGED

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

        # Set taget level and max step limit 
        speed_layout = QHBoxLayout()

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Target Tank Level")

        self.btnSetSpeed = QPushButton("Set Level")
        self.btnSetSpeed.clicked.connect(self.set_target_level)

        self.step_limit_input = QLineEdit()
        self.step_limit_input.setPlaceholderText("Max Step Limit")

        self.btnSetStepLimit = QPushButton("Set Max Steps")
        self.btnSetStepLimit.clicked.connect(
            lambda: self.motor.set_max_step_limit(self.step_limit_input.text())
        )

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.btnSetSpeed)
        speed_layout.addWidget(self.step_limit_input)
        speed_layout.addWidget(self.btnSetStepLimit)

        layout.addLayout(speed_layout)

        # Graph 
        self.plot_graph = pg.PlotWidget()
        layout.addWidget(self.plot_graph)

        self.setup_plot()

        self.target_line = pg.InfiniteLine(
            pos=0,
            angle=0,
            pen=pg.mkPen('g', width=2, style=Qt.DashLine),
            name="target"
        )
        self.plot_graph.addItem(self.target_line)

        self.update()

        # Data storge for each plot 
        self.start_time = time.time()

        self.time_data = deque(maxlen=30)
        self.value_A = deque(maxlen=30)
        self.value_B = deque(maxlen=30)

        for _ in range(30):
            self.time_data.append(0)
            self.value_A.append(0)
            self.value_B.append(0)

        # plotting the graph
        self.line_A = self.plot_graph.plot(
            self.time_data, self.value_A, name="level", pen="r"
        )

        self.line_B = pg.PlotCurveItem(
            list(self.time_data), list(self.value_B), pen="b", name="steps"
        )
        self.viewbox_B.addItem(self.line_B)

    def start_pressed(self):
        self.start_time = time.time()

        self.csv_saved = False
        self.record_time.clear()
        self.record_A.clear()
        self.record_B.clear()

        self.start_callback()

    def setup_plot(self):
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle("Measured Vs Target Fluid Level", color="b", size="15pt")

        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Fluid Level", **styles)
        self.plot_graph.setLabel("bottom", "Time (s)", **styles)

        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.addLegend()

        self.plot_graph.setYRange(0, 1100)
        self.plot_graph.enableAutoRange(axis='y', enable=False)

        self.plot_graph.showAxis('right')
        self.plot_graph.setLabel('right', 'Stepper Motor Position (Steps)', color='blue')
        self.plot_graph.getAxis('right').setPen('b')

        self.viewbox_B = pg.ViewBox()
        self.plot_graph.scene().addItem(self.viewbox_B)

        self.plot_graph.getAxis('right').linkToView(self.viewbox_B)
        self.viewbox_B.setXLink(self.plot_graph)

        self.viewbox_B.setYRange(0, 50)
        self.viewbox_B.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)

        self.plot_graph.getViewBox().sigResized.connect(self.update_views)

        self.update_views()

    def update_views(self):
        self.viewbox_B.setGeometry(self.plot_graph.getViewBox().sceneBoundingRect())
        self.viewbox_B.linkedViewChanged(
            self.plot_graph.getViewBox(), self.viewbox_B.XAxis
        )

    def set_target_level(self):
        try:
            value = float(self.speed_input.text())
            self.target_value = value

            self.motor.set_target_tank_level(value)
            self.target_line.setValue(value)

        except ValueError:
            print("Invalid target level")

    def register_stream(self, cs_pin, router):
        self.cs_pin = cs_pin

        router.register(
            cs_pin,
            0x05,
            self.receive_data
        )

    def receive_data(self, data):
        sensor, steps = data

        t = time.time() - self.start_time

        self.time_data.append(t)
        self.value_A.append(sensor)
        self.value_B.append(steps)

        if t <= 60:
            self.record_time.append(t)
            self.record_A.append(sensor)
            self.record_B.append(steps)

        if time.time() - self.last_plot_time > 0.05:
            self.line_A.setData(list(self.time_data), list(self.value_A))
            self.line_B.setData(list(self.time_data), list(self.value_B))
            self.last_plot_time = time.time()

        if t >= 60 and not self.csv_saved:
            self.save_60s_csv()
            self.load_csv_graph()
            self.csv_saved = True

    # Disso related code 

    # def save_60s_csv(self):
    #     filename = os.path.join(os.getcwd(), "valve_data.csv")

    #     with open(filename, "w", newline="") as f:
    #         writer = csv.writer(f)
    #         writer.writerow(["Time", "Sensor", "Steps"])

    #         for t, a, b in zip(self.record_time, self.record_A, self.record_B):
    #             writer.writerow([t, a, b])

    #     print("Valve 60s data saved")

  
    # def load_csv_graph(self):
    #     filename = os.path.join(os.getcwd(), "valve_data.csv")
    #     if not os.path.exists(filename):
    #         return

    #     t, a, b = [], [], []

    #     with open(filename, "r") as f:
    #         reader = csv.reader(f)
    #         next(reader)
    #         for row in reader:
    #             t.append(float(row[0]))
    #             a.append(float(row[1]))
    #             b.append(float(row[2]))

    #     self.csv_window = QWidget()
    #     self.csv_window.setWindowTitle("Valve 60s Data")

    #     layout = QVBoxLayout(self.csv_window)
    #     plot = pg.PlotWidget()
    #     layout.addWidget(plot)

    #     plot.setBackground("w")
    #     plot.setTitle("Saved 60 Second Valve Data", color="b")
    #     plot.setLabel("left", "Fluid Level", color="red")
    #     plot.setLabel("bottom", "Time (s)")
    #     plot.showGrid(x=True, y=True)
    #     plot.addLegend()

    #     line_a = plot.plot(t, a, pen="r", name="level")

     
        # plot.showAxis('right')
        # plot.setLabel('right', 'Stepper Motor Position (Steps)', color='blue')
        # plot.getAxis('right').setPen('b')

        # viewbox = pg.ViewBox()
        # plot.scene().addItem(viewbox)

        # plot.getAxis('right').linkToView(viewbox)
        # viewbox.setXLink(plot)

    
        # line_b = pg.PlotCurveItem(t, b, pen="b", name="steps")
        # viewbox.addItem(line_b)

        # def update_views():
        #     viewbox.setGeometry(plot.getViewBox().sceneBoundingRect())
        #     viewbox.linkedViewChanged(plot.getViewBox(), viewbox.XAxis)

        # plot.getViewBox().sigResized.connect(update_views)
        # update_views()

        # self.csv_window.resize(800, 500)
        # self.csv_window.show()

    
    def push_settings(self):
        self.motor.set_target_tank_level(self.speed_input.text())
        self.motor.set_max_step_limit(self.step_limit_input.text())
        self.motor.set_sensor(self.sensor_input.text())


class Peristaltic(QWidget):
    def __init__(self, motor, start_callback):
        super().__init__()

        self.motor = motor
        self.start_callback = start_callback

        self.last_plot_time = 0
        self.target_value = 0
        self.csv_saved = False   
        self.record_time = []
        self.record_value = []

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.start_pressed)

        self.btnStop = QPushButton("Stop")
        self.btnStop.clicked.connect(self.motor.stop_motor)

        top_layout.addWidget(self.btnStart)
        top_layout.addWidget(self.btnStop)

        layout.addLayout(top_layout)

        sensor_layout = QHBoxLayout()

        self.sensor_input = QLineEdit()
        self.sensor_input.setPlaceholderText("Sensor Pin")

        sensor_layout.addWidget(QLabel("Sensor Pin:"))
        sensor_layout.addWidget(self.sensor_input)

        layout.addLayout(sensor_layout)

    #   define target flow rate 
        self.flow_layout = QHBoxLayout()

        self.flow_input = QLineEdit()
        self.flow_input.setPlaceholderText("Flow Rate")

        self.flow_layout.addWidget(self.flow_input)

        layout.addLayout(self.flow_layout)

        # define PID inputs for tuning 
        self.pid_layout = QHBoxLayout()

        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("P")

        self.i_input = QLineEdit()
        self.i_input.setPlaceholderText("I")

        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("D")

        self.pid_layout.addWidget(self.p_input)
        self.pid_layout.addWidget(self.i_input)
        self.pid_layout.addWidget(self.d_input)

        layout.addLayout(self.pid_layout)

        self.plot_graph = pg.PlotWidget()
        layout.addWidget(self.plot_graph)

        self.setup_plot()

        self.target_line = pg.InfiniteLine(
            pos=0,
            angle=0,
            pen=pg.mkPen('g', width=2, style=Qt.DashLine),
            name="target"
        )
        self.plot_graph.addItem(self.target_line)

        self.start_time = time.time()

        self.time_data = deque(maxlen=30)
        self.value_A = deque(maxlen=30)

        for i in range(30):
            self.time_data.append(i)
            self.value_A.append(0)

        self.line_A = self.plot_graph.plot(
            self.time_data, self.value_A, name="Flow Rate", pen="r"
        )

    def setup_plot(self):
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle("Motor Flow Rate vs Time", color="b", size="20pt")

        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Flow Rate (ml/s)", **styles)
        self.plot_graph.setLabel("bottom", "Time (s)", **styles)

        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        self.plot_graph.setYRange(0, 15)

    def start_pressed(self):
        try:
            value = float(self.flow_input.text())
            self.target_value = value

            self.motor.set_flow_rate(value)
            self.target_line.setValue(value)

            self.start_time = time.time()   
            self.csv_saved = False          
            self.record_time = []
            self.record_value = []      

            self.start_callback()

        except ValueError:
            print("Invalid flow rate")

    def register_stream(self, cs_pin, router):
        self.cs_pin = cs_pin

        router.register(
            cs_pin,
            0x06,
            self.receive_data
        )

    def receive_data(self, value):
        t = time.time() - self.start_time

        self.time_data.append(t)
        self.value_A.append(value)

        if t <= 60:
            self.record_time.append(t)
            self.record_value.append(value)

        if time.time() - self.last_plot_time > 0.05:
            self.line_A.setData(self.time_data, self.value_A)
            self.last_plot_time = time.time()

      
        if t >= 60 and not self.csv_saved:
            self.save_60s_csv()
            self.load_csv_graph()
            self.csv_saved = True

    def activated(self, index):
        self.motor.set_speed_unit(index)

    def push_settings(self):
        self.motor.set_sensor(self.sensor_input.text())
        self.motor.set_flow_rate(self.flow_input.text())
        self.motor.set_pid(
            self.p_input.text(),
            self.i_input.text(),
            self.d_input.text()
        )

    # Disso related code 

    # def save_60s_csv(self):
    #     import csv
    #     import os

    #     filename = os.path.join(os.getcwd(), "flow_data.csv")

    #     with open(filename, "w", newline="") as file:
    #         writer = csv.writer(file)
    #         writer.writerow(["Time (s)", "Value A"])

    #         for t, v in zip(self.record_time, self.record_value):
    #             writer.writerow([t, v])

    #     print("Saved first 60 seconds")

    # def load_csv_graph(self):
    #     import csv
    #     import os

    #     filename = os.path.join(os.getcwd(), "flow_data.csv")

    #     if not os.path.exists(filename):
    #         return

    #     x = []
    #     y = []

    #     with open(filename, "r") as file:
    #         reader = csv.reader(file)
    #         next(reader)

    #         for row in reader:
    #             x.append(float(row[0]))
    #             y.append(float(row[1]))

    #     self.csv_window = QWidget()
    #     self.csv_window.setWindowTitle("Saved CSV Graph")

    #     layout = QVBoxLayout(self.csv_window)

    #     self.csv_plot = pg.PlotWidget()
    #     layout.addWidget(self.csv_plot)

    #     self.csv_plot.setBackground("w")
    #     self.csv_plot.setTitle("Saved 60 Second Flow Data")
    #     self.csv_plot.setLabel("left", "Flow Rate")
    #     self.csv_plot.setLabel("bottom", "Time (s)")
    #     self.csv_plot.showGrid(x=True, y=True)

    #     self.csv_plot.plot(x, y, pen="b")

    #     self.csv_window.resize(800, 500)
    #     self.csv_window.show()