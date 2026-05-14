#include "valve_control.h"
#include "motor_base.h"

void ValveControl::update(MotorBase& motor)
{
    static float integral = 0;
    static unsigned long last_time = 0;
    static int last_speed = -1;
    
    static int last_target = 0;

    // step tracking (starts at home = 0)
    static long last_index = 0;
    static int num_of_steps = 0;

    // ramp state
    static float ramp_target = 0;

    int sensor = motor.analogValue;
    int target = motor.target_tank_level;

    // Record time 
    unsigned long now = micros();
    float dt = (now - last_time) / 1000000.0f;
    last_time = now;

    if (dt <= 0) return;

    // Detect new target
    if (target != last_target)
    {
        integral = 0;

        // start ramp from previous target
        ramp_target = last_target;
    }
 
    float ramp_rate = 50.0f;  // units per second (TUNE THIS)

    float diff = target - ramp_target;
    float step = ramp_rate * dt;

    if (diff > step)
    {
        ramp_target += step;
    }
    else if (diff < -step)
    {
        ramp_target -= step;
    }
    else
    {
        ramp_target = target;  
    }

    // update last target AFTER ramp logic
    last_target = target;

    // calculate error 
    float error = ramp_target - sensor;

    // calculate integral 
    integral += error * dt;

    if (integral > 500) integral = 500;
    if (integral < -500) integral = -500;

    // Pi output
    float output = (0.1 * error) + (0.1 * integral);

    if (output > 30) output = 30;
    if (output < -30) output = -30;

    // sorts motor direction
    motor.direction = (output > 0) ? 1 : -1;

    // speed
    int speed = abs(output);

    // step limit logic 
    bool at_upper_limit = (num_of_steps >= motor.step_limit);
    bool at_lower_limit = (num_of_steps <= 0);

    if ((at_upper_limit && motor.direction == 1) ||
        (at_lower_limit && motor.direction == -1))
    {
        speed = 0;
    }

    if (speed != last_speed)
    {
        motor.setSpeed(speed);
        last_speed = speed;
    }

    // step counting
    if (motor.direction == 1)
    {
        if (motor.current_index < last_index)
        {
            num_of_steps++;
        }
    }
    else
    {
        if (motor.current_index > last_index)
        {
            num_of_steps--;
        }
    }

    last_index = motor.current_index;

    // ensures motor is updated 
    if (speed > 0)
    {
        motor.step();
    }

    // sends data to rapsberry pi 
    static elapsedMillis sendTimer;

    if (sendTimer < 50) return;
    sendTimer = 0;

    uint8_t cs_pin = motor.csPin;
    uint8_t graph_mode = 5;

    Serial.write(0xAB);
    Serial.write(graph_mode);
    Serial.write(cs_pin);

    Serial.write((sensor >> 8) & 0xFF);
    Serial.write(sensor & 0xFF);

    Serial.write(num_of_steps);
    Serial.write(0x54);
}