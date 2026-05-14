#include "calibration.h"
#include "motor_base.h"

elapsedMillis sendTimer;

CalPoint calibrationTable[12];
int calibrationSize = 0;
bool calibrationReady = false;

// This script is still in the middle of development stages and should not be used as
// a reference point to make a motor C++ script 


void Calibration::update(MotorBase& motor)
{
    static int current_speed = 10;
    static int last_speed = -1;
    static elapsedMillis stepTimer;

    static float sum = 0;
    static int count = 0;

    
    if (calibrationReady)
        return;

   
    if (stepTimer > 2000)
    {
        if (count > 0 && calibrationSize < 12)
        {
            float avg = sum / count;

            calibrationTable[calibrationSize].speed = current_speed;
            calibrationTable[calibrationSize].sensor = avg;
            calibrationSize++;
        }

        sum = 0;
        count = 0;

        current_speed += 10;

        if (current_speed > 120)
        {
            calibrationReady = true;
            return;
        }

        stepTimer = 0;
    }

   
    if (current_speed != last_speed)
    {
        motor.setSpeed(current_speed);
        last_speed = current_speed;
    }

    motor.step();

  
    int reading = motor.analogValue;
    float sensor = sqrt(max(0, reading - 6));

    sum += sensor;
    count++;

    if (sendTimer < 50) return;
    sendTimer = 0;

  
    uint8_t value_A = motor.phaseA_output;
    uint8_t value_B = motor.phaseB_output;
    uint8_t cs_pin = motor.csPin;
    uint8_t graph_mode = 1;

    Serial.write(0xAB);
    Serial.write(graph_mode);
    Serial.write(cs_pin);

    Serial.write((value_A >> 8) & 0xFF);
    Serial.write(value_A & 0xFF);

    Serial.write((value_B >> 8) & 0xFF);
    Serial.write(value_B & 0xFF);



    Serial.write(0x54);
}
