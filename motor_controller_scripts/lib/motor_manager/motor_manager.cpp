#include "motor_manager.h"
#include "calibration.h"
#include "basic_motor.h"
#include "index_position.h"
#include "syringe_pump.h"
#include "valve_control.h"
#include "peristaltic.h"

// To add another mode must define below with everything else 
// commands go through motor manager 

Calibration calibration;
IndexPosition indexPosition;
BasicMotor basicMotor;
SyringePump syringePump;
ValveControl valveControl;
Peristaltic peristaltic;

// Below are definitions which sort the number of motors which are active on the teensy 
// central part being the motorUsed varaible which is a pointer to the place where
// information about each motor is stored 

MotorManager::MotorManager()
{
    motorCount = 0;

    for(size_t i=0;i<MAX_MOTORS;i++)
        motorUsed[i] = false;
}

MotorBase* MotorManager::addMotor(uint8_t csPin, uint16_t speed)
{
    MotorBase* existing = findMotor(csPin);

    if(existing) return existing;

    if(motorCount >= MAX_MOTORS) return nullptr;

    motors[motorCount].init(csPin, speed);

    motorUsed[motorCount] = true;

    motorCount++;

    return &motors[motorCount - 1];
}

MotorBase* MotorManager::findMotor(uint8_t csPin)
{
    for(size_t i=0;i<motorCount;i++)
        if(motorUsed[i] && motors[i].getCSPin()==csPin)
            return &motors[i];

    return nullptr;
}

void MotorManager::deleteMotor(uint8_t csPin)
{
    for(size_t i=0;i<motorCount;i++)
    {
        if(motorUsed[i] && motors[i].getCSPin()==csPin)
        {
            motors[i].stop();
            motorUsed[i] = false;
        }
    }
}

void MotorManager::handleCommand(uint8_t csPin,
                                 uint8_t command,
                                 uint16_t speed,
                                 uint8_t direction,
                                 uint8_t mode,
                                 uint8_t sensor,
                                 uint8_t speed_unit,
                                 uint16_t tank_level,
                                 uint8_t step_limit,
                                 uint8_t flow_rate,
                                 uint16_t kp,
                                 uint16_t ki,
                                 uint16_t kd,
                                 uint16_t diameter,
                                 uint16_t lead,
                                 uint16_t volume,
                                 uint16_t syringe_flow)
{
    // Below is the opposite of the packet creation, 
    // byte values are parsed to differeent definitions not defined in this script 
    // but defined in motor base or initiating the mode scripts 
    
    if(command == 0x04)
    {
        deleteMotor(csPin);
        return;
    }

    MotorBase* motor = findMotor(csPin);

    if(!motor)
        motor = addMotor(csPin, speed);

    if(!motor) return;

    switch(command)
    {
        case 0x01: motor->setSpeed(speed); break;

        case 0x02:
            motor->start(speed);
           
        break;

        case 0x03: motor->stop(); break;

        case 0x07:
            motor->setMode(&indexPosition);  
            motor->startHoming();
            break;

        case 0x08:
            motor-> disable();
            return;



    }


    switch(direction)
    {
        case 0x05: motor->reverse(-1); break;  // reverse the motor to clockwise direction facing motor 

        case 0x06: motor->reverse(1); break;   // undose the reversal to inital direction (anti clockwise)
    }

    switch(mode)
    {
        case 0x01:   // Calibration (GUI)
            motor->setMode(&calibration);
            break;
        
        case 0x02:   // Index Position (GUI)
            motor->setMode(&indexPosition);
            // for a mode the sensor needs to defined whether its analouge 
            // (pressure or potentiometer) or discrete (light gate sensor)
            motor->isAnalogSensor = false;
            break;

        case 0x03:   // Basic Rotation (GUI)
            motor->setMode(&basicMotor);
            break;

        case 0x04:   // Syringe Pump (GUI)
            motor->setMode(&syringePump);     
            break;

        case 0x05:   // ValveControl (GUI)
            motor->setMode(&valveControl);
            motor->isAnalogSensor = true;
            motor->getStepLimit(step_limit);
            break;

        case 0x06:   // Peristaltic (GUI)
            motor->setMode(&peristaltic);
            motor->isAnalogSensor = true;
            break;

    }

    switch(speed_unit)
    {
        case 0x01: motor->setUnit(speed_unit); break;  // reverse the motor to clockwise direction facing motor 

        case 0x02: motor->setUnit(speed_unit); break;   // undose the reversal to inital direction (anti clockwise)
    }


    // This just passes on the remaining varaibles to motorBase
    motor->setSensorPin(sensor);
    motor->getStepLimit(step_limit);
    motor->getTankLevel(tank_level);
    motor->getFlowRate(flow_rate);
    motor->getPID(kp,ki,kd);
    motor->getSyringeParams(diameter,lead,volume,syringe_flow);

}

void MotorManager::updateAllMotors()
{
    for(size_t i=0;i<motorCount;i++)
    {
        if(motorUsed[i])
            motors[i].update();
    }
}