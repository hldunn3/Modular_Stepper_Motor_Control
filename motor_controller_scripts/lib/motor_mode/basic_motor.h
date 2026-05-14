#pragma once
#include "motor_mode.h"

class MotorBase;

class BasicMotor : public MotorMode {
public:
    void update(MotorBase& motor) override;
};