#pragma once
#include "motor_mode.h"

class MotorBase;

struct CalPoint {
    int speed;
    float sensor;
};

extern CalPoint calibrationTable[12];
extern int calibrationSize;
extern bool calibrationReady;

class Calibration : public MotorMode {
public:
    void update(MotorBase& motor) override;
};