#pragma once
#include <Arduino.h>
#include "motor_base.h"

#define MAX_MOTORS 8

class MotorManager {

public:

    MotorManager();

    MotorBase* addMotor(uint8_t csPin, uint16_t speed);

    MotorBase* findMotor(uint8_t csPin);

    void deleteMotor(uint8_t csPin);

    void handleCommand(uint8_t csPin,
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
                       uint16_t syringe_flow);

    void updateAllMotors();


private:

    MotorBase motors[MAX_MOTORS];

    bool motorUsed[MAX_MOTORS];

    size_t motorCount;

    int mode; 

    uint16_t kp;
    uint16_t ki;
    uint16_t kd;


};