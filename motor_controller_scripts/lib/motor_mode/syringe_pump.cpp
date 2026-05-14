#include "syringe_pump.h"
#include "motor_base.h"
#include <math.h>

void SyringePump::update(MotorBase& motor)
{

static bool first_run = true;
static int num_of_cycles = 0;
static int revs = 0;
static int last_index = 0;
static int cycles_per_revs = motor.num_step/4;

float diameter_mm = motor.diameter / 100.0f;
float lead_mm = motor.lead / 100.0f;
float volume_mL = motor.volume / 100.0f;
float flow_mL_s = motor.syringe_flow / 100.0f;

// calc number of revs needed (ready to convert to cycles)
float area = (M_PI * diameter_mm * diameter_mm) / 4.0f;

float required_revs = (volume_mL * 1000) / (lead_mm * area); 

// convert required revs to cycles 
long required_cycles = required_revs * cycles_per_revs;

// calc reves per second from flow rate 
float revs_per_sec = (flow_mL_s * 1000) / (lead_mm * area);

// convert revs per second to cycle per second 
int cycle_per_second = revs_per_sec * cycles_per_revs;


if (first_run)
{
    last_index = motor.current_index;
    motor.start(cycle_per_second);
    first_run = false;
}

motor.step();

if (motor.direction == 1)
{
    
    if (motor.current_index < last_index)
    {
        if ((last_index - motor.current_index) > 5)
        {
            num_of_cycles++;
        }
    }
}
else if (motor.direction == -1)
{
    
    if (motor.current_index > last_index)
    {
        if ((motor.current_index - last_index) > 5)
        {
            num_of_cycles++;
        }
    }
}

// count revolutions
if (num_of_cycles >= required_cycles)
{
   motor.stop();
   first_run = true;
   num_of_cycles = 0;

}

last_index = motor.current_index;

}