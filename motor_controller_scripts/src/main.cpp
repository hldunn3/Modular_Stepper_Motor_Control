#include <Arduino.h>
#include <SPI.h>
#include <IntervalTimer.h>

#include "motor_manager.h"

MotorManager motorManager;

void setup()
{
    Serial.begin(115200);
    SPI1.begin();
    SPI1.beginTransaction(SPISettings(20000000, MSBFIRST, SPI_MODE0));
    
}

void loop() {

   
    static elapsedMicros loopTime;
    loopTime = 0;

    // select command packet with the correct start byte 
    if (Serial.peek() == 0xAA)
    {
        Serial.read();

        int cs       = Serial.read();
        int command  = Serial.read();
        int highByte = Serial.read();
        int lowByte  = Serial.read();
        int direction = Serial.read();
        int mode = Serial.read();
        int sensor = Serial.read();
        int speed_unit = Serial.read();
        int tank_high_byte = Serial.read();
        int tank_low_byte = Serial.read();
        int step_limit = Serial.read();
        int flow_rate = Serial.read();
        int kp_high = Serial.read();
        int kp_low  = Serial.read();
        int ki_high = Serial.read();
        int ki_low  = Serial.read();
        int kd_high = Serial.read();
        int kd_low  = Serial.read();

        int diam_high = Serial.read();
        int diam_low  = Serial.read();
        int lead_high = Serial.read();
        int lead_low  = Serial.read();
        int vol_high = Serial.read();
        int vol_low  = Serial.read();
        int flow_high = Serial.read();
        int flow_low  = Serial.read();

        int endByte  = Serial.read();

        if (endByte == 0x55)
        {
            // translate the 16 bit value commands to one varaible again 
            uint16_t speed = ((uint16_t)highByte << 8) | lowByte;
            uint16_t tank_level = ((uint16_t)tank_high_byte << 8) | tank_low_byte;

            uint16_t kp = ((uint16_t)kp_high << 8) | kp_low;
            uint16_t ki = ((uint16_t)ki_high << 8) | ki_low;
            uint16_t kd = ((uint16_t)kd_high << 8) | kd_low;

            uint16_t diameter = ((uint16_t)diam_high << 8) | diam_low;
            uint16_t lead     = ((uint16_t)lead_high << 8) | lead_low;
            uint16_t volume   = ((uint16_t)vol_high << 8) | vol_low;
            uint16_t syringe_flow = ((uint16_t)flow_high << 8) | flow_low;
            // all commands are parsed onto the handle command definition in motor manager 
            motorManager.handleCommand(
                (uint8_t)cs,
                (uint8_t)command,
                speed,
                direction,
                mode,
                sensor,
                speed_unit,
                tank_level,
                step_limit,
                flow_rate,
                kp,
                ki,
                kd,
                diameter,
                lead,
                volume,
                syringe_flow);       
        }
    }

    motorManager.updateAllMotors();


    // disso related code
//    uint32_t exec_us = loopTime;

//     static elapsedMillis sendTimer;
//     if (sendTimer < 50) return;   // send every 50 ms (~20 Hz)
//     sendTimer = 0;

//     uint8_t graph_mode = 7;   // performance mode
//     uint8_t cs_pin = 0;       // system-level

//     Serial.write(0xAB);
//     Serial.write(graph_mode);
//     Serial.write(cs_pin);

//     Serial.write((exec_us >> 8) & 0xFF);
//     Serial.write(exec_us & 0xFF);

//     Serial.write(0x54);
}
