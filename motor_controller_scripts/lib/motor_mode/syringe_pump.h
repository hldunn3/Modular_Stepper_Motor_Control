#pragma once

#include "motor_mode.h"

class SyringePump : public MotorMode {
public:
    void update(MotorBase& motor) override;

private:
    long cycles_completed = 0;
    int last_index = 0;
};