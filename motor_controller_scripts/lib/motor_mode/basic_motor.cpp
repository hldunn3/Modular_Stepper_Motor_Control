#include "basic_motor.h"
#include "motor_base.h"

void BasicMotor::update(MotorBase& motor)
{   
    // As basic a script needs to be, this is really running of motorBase commands 
    // with no higher order logic inplace
    motor.step();
}


