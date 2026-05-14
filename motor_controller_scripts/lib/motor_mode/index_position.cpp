#include "index_position.h"
#include "motor_base.h"
#include <Arduino.h>

void IndexPosition::update(MotorBase& motor)
{
    if(motor.isHoming)
    {
        motor.step();  

        if(motor.indexTriggered)
        {
            motor.stop();

            motor.position = 0;
            motor.isHoming = false;

            Serial.println("HOMED");
        }

        return;  
    }

    static int indexCount = 0;

    motor.step();

    if(motor.indexTriggered)
    {
        indexCount++;

        Serial.print("Index count: ");
        Serial.println(indexCount);
    }

    
}

        