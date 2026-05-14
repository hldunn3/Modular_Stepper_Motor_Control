import serial

# Update to your Arduino port
# ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_18660570-if00', 115200, timeout=1)
ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_18671260-if00', 115200, timeout=1)

"""These definintions are called in the tab and main window scripts, this is where varaibles are stored and ready to be 
sent to the teensy, some varibles need conversion to different orders of magnitude so decimal numbers can also be sent 
all values are converted to a byte number, this even includes catagoric commands and have a number assoicted with that name"""


class Packet_Creation:
    def __init__(self, CS=None):
        self.CS = CS                  # Current CS pin (stored, not sent)
        self.speed_value = 0           # 0–4095 DAC value (stored)
        self.is_running = False        # track running state
        self.direction = 0x06
        self.mode = 0x01
        self.sensor = 0 
        self.unit = 1
        self.tank_level = 0
        self.step_limit = 0
        self.flow_rate = 0 
        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.diameter = 0
        self.lead = 0
        self.target_volume = 0
        self.syringe_flow = 0

    def set_cs_pin(self, cs_text):
        # Delete old motor first
        if self.CS is not None:
            try:
                old_cs = int(self.CS)
                packet = bytes([0xAA, old_cs, 0x04, 0x00, 0x00, 0x55])  # 0x04 = DELETE
                ser.write(packet)
            except ValueError:
                pass

        # Store new CS pin
        try:
            self.CS = int(cs_text)
        except ValueError:
            pass

    def set_mode(self, mode):
        self.mode = mode

    def set_sensor(self, sensor):
        try:
            self.sensor = int(sensor)
        except:
            self.sensor = 0

        if self.sensor == 0:
            self.sensor = 254

    def apply_settings(self):
        self.send_packet(0x01)   # update command
        

    def set_speed_from_text(self, speed_text):
        try:
            frequency = int(speed_text)
        except ValueError:
            return
        self.speed_value = frequency # old varaible names just used to define speed  

    def set_target_tank_level(self, tank_level):
       
        try:
              self.tank_level = int(tank_level)
        except ValueError:
            return

    def set_max_step_limit(self, step_limit):
        try:
              self.step_limit = int(step_limit)
        except ValueError:
            return
    def set_flow_rate(self, flow_rate):
        try:
              self.flow_rate = int(flow_rate)   
             
        except ValueError:
            return
    
    def set_speed_unit(self,index):
        index += 1        # index starts from 0, needs to start from 1. 
        self.unit = index
        print(index, 'from packet')
    
    def set_pid(self, p, i, d):
        # multiplied by 100 as to send decimal numbers, converted back to decimal on the teensy side 
        try:
            self.kp = int(float(p) * 100)
        except:
            self.kp = 0

        try:
            self.ki = int(float(i) * 100)
        except:
            self.ki = 0

        try:
            self.kd = int(float(d) * 100)
        except:
            self.kd = 0

    def set_syringe_params(self, d, p, v, q):
        try:
            self.diameter = int(float(d) * 100)   # scale for precision
        except:
            self.diameter = 0

        try:
            self.lead = int(float(p) * 100)
        except:
            self.lead = 0

        try:
            self.target_volume = int(float(v) * 100)
        except:
            self.target_volume = 0

        try:
            self.syringe_flow = int(float(q) * 100)
        except:
            self.syringe_flow = 0

    def start_motor(self):
        self.apply_settings()      # send current values first
        self.send_packet(0x02)     # then start
        self.is_running = True

    def stop_motor(self):
        self.send_packet(0x03)  # stop command
        self.is_running = False

    def return_home(self):
        self.send_packet(0x07)
        self.is_running = True


    def disable_motor(self,state):
        self.is_running = True
        if state:       # reverse
            # self.send_packet(0x05)  # Reverse command 
            self.send_packet(0x08)

    def reverse_motor(self,state):
        """this function can be with the overall command if you want to reverse the motor instanlty 
        from pressing the tick box, will have to use another byte if you want to send a seperate stored function 
        which may be the case as people may want to set it in revese """
        self.is_running = True
        if state:       # reverse
            # self.send_packet(0x05)  # Reverse command 
            self.direction = 0x05
        else:
            # self.send_packet(0x06)   # forward  
            self.direction = 0x06



    def send_packet(self, command):
            
            if self.CS is None:
                return

            try:
                cs_pin = int(self.CS)
            except (ValueError, TypeError):
                return
            
            

            high_byte = (self.speed_value >> 8) & 0xFF
            low_byte  = self.speed_value & 0xFF
            # speed_value = self.speed_value

            tank_high_byte = (self.tank_level >> 8) & 0xFF
            tank_low_byte  = self.tank_level & 0xFF

            kp_high = (self.kp >> 8) & 0xFF
            kp_low  = self.kp & 0xFF

            ki_high = (self.ki >> 8) & 0xFF
            ki_low  = self.ki & 0xFF

            kd_high = (self.kd >> 8) & 0xFF
            kd_low  = self.kd & 0xFF

            diam_high = (self.diameter >> 8) & 0xFF
            diam_low  = self.diameter & 0xFF

            lead_high = (self.lead >> 8) & 0xFF
            lead_low  = self.lead & 0xFF

            vol_high = (self.target_volume >> 8) & 0xFF
            vol_low  = self.target_volume & 0xFF

            flow_high = (self.syringe_flow >> 8) & 0xFF
            flow_low  = self.syringe_flow & 0xFF

            packet = bytes([
                0xAA,
                cs_pin,
                command,
                high_byte,
                low_byte,
                self.direction,
                self.mode,
                self.sensor,
                self.unit,
                tank_high_byte,
                tank_low_byte,
                self.step_limit,
                self.flow_rate,

                kp_high,
                kp_low,
                ki_high,
                ki_low,
                kd_high,
                kd_low,

                diam_high,
                diam_low,
                lead_high,
                lead_low,
                vol_high,
                vol_low,
                flow_high,
                flow_low,
                
                0x55
            ])

    

            ser.write(packet)
            print("CS Pin: ",cs_pin)
            print("Command: ",command)
            print("High Byte: ",high_byte)
            print("Low Byte: ",low_byte)
            print("Direction ",self.direction)
            print("Mode: ",self.mode)
            print("Sensor: ",self.sensor)
            print("Unit: ",self.unit)
            print("tank_high_byte: ",tank_high_byte)
            print("tank_low_byte: ",tank_low_byte)
            print("Flow rate: ",self.flow_rate)
            print("Diameter:", self.diameter)
            print("Lead:", self.lead)
            print("Target Volume:", self.target_volume)
            print("Syringe Flow:", self.syringe_flow)



        
        
