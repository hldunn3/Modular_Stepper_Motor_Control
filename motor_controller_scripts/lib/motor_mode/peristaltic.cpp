#include "peristaltic.h"
#include "motor_base.h"

void Peristaltic::update(MotorBase& motor)
{
    static unsigned long last_time = 0;
    static float integral = 0;

    static int last_speed = -1;

    static int last_index = 0;
    static int cycle_index = 0;

    static float speed_table[50];
    static bool initialized = false;

    static float cycle_sum = 0;
    static int cycle_samples = 0;

    static float ramp_target = 0;
    static float last_target = 0;

    if (!initialized)
    {
        for (int i = 0; i < 50; i++)
            speed_table[i] = 35;   // baseline

        initialized = true;
    }


    // record of time 
    unsigned long now = micros();
    float dt = (now - last_time) / 1000000.0f;
    last_time = now;

    if (dt <= 0) return;

    // Sensor configuration 
    int reading = motor.analogValue;
    float sensor = sqrt(reading);

    float target = motor.flow_rate;

    //  ramp target section 
    if (target != last_target)
    {
        ramp_target = last_target;
        integral = 0;  // reset PI on change
    }

    float ramp_rate = 0.5f;  // tune this
    float diff = target - ramp_target;
    float step = ramp_rate * dt;

    if (diff > step)       ramp_target += step;
    else if (diff < -step) ramp_target -= step;
    else                   ramp_target = target;

    last_target = target;

    // Collect cyc;le data 
    cycle_sum += sensor;
    cycle_samples++;

    // end of cycle
    if (motor.current_index < last_index)
    {
        if (cycle_samples > 0)
        {
            float cycle_avg = cycle_sum / cycle_samples;

            float error = ramp_target - cycle_avg;

            // learning rate
            float learn_gain = 1.0f;   // tune (0.2–1.0)

            float adjust = error * learn_gain;

            // smooth averaging toward corrected value
            speed_table[cycle_index] += adjust * 0.5f;

            // clamp
            if (speed_table[cycle_index] > 120) speed_table[cycle_index] = 120;
            if (speed_table[cycle_index] < 0)   speed_table[cycle_index] = 0;
        }

        cycle_sum = 0;
        cycle_samples = 0;

        cycle_index = (cycle_index + 1) % 50;
    }

    last_index = motor.current_index;

    //  Global PI controller
    float kp = motor.kp / 100.0f;
    float ki = motor.ki / 100.0f;

    float error = ramp_target - sensor;

    integral += error * dt;

    // anti-windup 
    if (integral > 300) integral = 300;
    if (integral < -300) integral = -300;

    float pi_output = (kp * error) + (ki * integral);

    //  FINAL OUTPUT 
    float base_speed = speed_table[cycle_index];

    float output = base_speed + pi_output;

    if (output > 120) output = 120;
    if (output < 0)   output = 0;

    int speed = (int)output;

    // Motor commands
    if (speed != last_speed)
    {
        motor.setSpeed(speed);
        last_speed = speed;
    }

    if (speed > 0)
    {
        motor.step();
    }

    // Send data back to raspberry pi 
    static elapsedMillis sendTimer;
    if (sendTimer < 50) return;
    sendTimer = 0;

    uint8_t cs_pin = motor.csPin;
    uint8_t graph_mode = 6;

    Serial.write(0xAB);
    Serial.write(graph_mode);
    Serial.write(cs_pin);

    int send_sensor = int(sensor * 100);

    Serial.write((send_sensor >> 8) & 0xFF);
    Serial.write(send_sensor & 0xFF);

    Serial.write(0x54);
}