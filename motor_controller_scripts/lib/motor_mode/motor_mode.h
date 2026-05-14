#pragma once

class MotorBase;

class MotorMode {
public:
    virtual void update(MotorBase& motor) = 0;
};