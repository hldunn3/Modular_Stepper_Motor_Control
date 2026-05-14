import serial
from PyQt5 import QtCore
import time

class SerialRouter(QtCore.QObject):
    """
    Script purly for getting data back from the teensy 
    and parsing the data to the correct motor and mode window

    Combined Serial Manager + Motor Router

    - Reads serial data
    - Parses packets
    - Routes to registered callbacks based on (cs_pin, mode)
    """

    def __init__(self, port):
        super().__init__()
     
        self.ser = serial.Serial(port, 115200, timeout=0)
     
        self.registry = {}   # (cs_pin, mode) -> callback

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.read_serial)
        self.timer.start()

    def register(self, cs_pin, mode, callback):
        self.registry[(cs_pin, mode)] = callback

  
    def route(self, cs_pin, mode, value):
        key = (cs_pin, mode)

        if key in self.registry:
            self.registry[key](value)

   
    def read_serial(self):
        while self.ser.in_waiting > 0:

            first = self.ser.read(1)

            if first != b'\xAB':
                continue

            mode_byte = self.ser.read(1)
            if len(mode_byte) == 0:
                continue
            mode = mode_byte[0]

            cs_byte = self.ser.read(1)
            if len(cs_byte) == 0:
                continue
            cs_pin = cs_byte[0]

            if mode == 0x05:   # Valve mode
                data = self.ser.read(4)

                if len(data) != 4:
                    continue

                sensor = (data[0] << 8) | data[1]
                steps = data[2]
                end = data[3]

                if end != 0x54:
                    continue

                self.route(cs_pin, mode, (sensor, steps))

            if mode == 0x06:   # peri mode
                data = self.ser.read(3)

                if len(data) != 3:
                    continue

                read_sensor = (data[0] << 8) | data[1]
                sensor = read_sensor/ 100 

                end = data[2]

                if end != 0x54:
                    continue

                self.route(cs_pin, mode, sensor)

            else:
                data = self.ser.read(5)

                if len(data) != 5:
                    continue

                value_A = (data[0] << 8) | data[1]
                value_B = (data[2] << 8) | data[3]
                end = data[4]

                if end != 0x54:
                    continue

                self.route(cs_pin, mode, (value_A, value_B))