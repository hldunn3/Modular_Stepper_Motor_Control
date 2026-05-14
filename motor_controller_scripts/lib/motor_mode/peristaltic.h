#pragma once
#include "motor_mode.h"

class MotorBase;

class Peristaltic : public MotorMode {
public:
    void update(MotorBase& motor) override;
};