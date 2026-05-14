#pragma once
#include "motor_mode.h"

class MotorBase;

class ValveControl : public MotorMode {
public:
    void update(MotorBase& motor) override;

    
private:
    int num_of_steps = 0;
    int revs = 0;
    int last_index = 0;

};