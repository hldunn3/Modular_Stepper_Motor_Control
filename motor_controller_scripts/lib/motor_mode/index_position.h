#pragma once
#include "motor_mode.h"

class MotorBase;

class IndexPosition : public MotorMode {
public:
    void update(MotorBase& motor) override;

private:

};