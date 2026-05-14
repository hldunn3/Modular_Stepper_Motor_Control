#include "motor_base.h"
#include "motor_mode.h"
#include "microstep_table.h"
#include <SPI.h>

#define USE_AD5689 1
#define _LDAC 2   // change if needed

MotorBase::MotorBase()
{
    csPin = 0;
    isRunning = false;

    direction = 1;
    phase = 0;

    speed_divide = 1;

    last_speed_step_time = 0;
    last_speed_step_index = 0;
    current_index = 0;

    phaseA_output = 32768;
    phaseB_output = 32768;

    currentMode = nullptr;

    sensorPin = 255;
    lastIndexState = false;
    indexTriggered = false;
    num_step = 200;
    unit = 1;
}

void MotorBase::init(uint8_t cs, uint16_t speed)
{
    csPin = cs;

    pinMode(_LDAC, OUTPUT);
    pinMode(csPin, OUTPUT);

    digitalWrite(csPin, HIGH);
    digitalWrite(_LDAC, HIGH);

    last_speed_step_time = micros();
    last_speed_step_index = 0;
    current_index = 0;

    setSpeed(speed);
}

void MotorBase::setMode(MotorMode* m)
{
    currentMode = m;
}

void MotorBase::start(uint16_t speed_start)
{
    isDisabled = false;   // re-enable
    isRunning = true;
    setSpeed(speed_start);
}

void MotorBase::stop()
{
    isRunning = false;
}

void MotorBase::disable()
{
    isDisabled = true;
    isRunning = false;
    currentMode = nullptr;

    phaseA_output = 0;
    phaseB_output = 0;

    writeDAC(0, 0);
}


void MotorBase::reverse(int num)
{
    direction = num;
    last_speed_step_index = current_index;
    last_speed_step_time = micros();
}

uint8_t MotorBase::getCSPin()
{
    return csPin;
}

void MotorBase::setSensorPin(uint8_t pin)
{
    sensorPin = pin;
}
void MotorBase::setUnit(uint8_t speed_unit)
{
    unit = speed_unit;

}
void MotorBase::startHoming()
{
    isHoming = true;
    isRunning = true;   // ensure motor moves
}

void MotorBase::getTankLevel(uint16_t manager_tank_level)
{
    target_tank_level = manager_tank_level;  
}

void MotorBase::getStepLimit(uint8_t manager_step_limit)
{
    step_limit = manager_step_limit;  
}

void MotorBase::getFlowRate(uint8_t manager_flow_rate)
{
    flow_rate = manager_flow_rate;  
}

void MotorBase::getPID(uint16_t manager_kp, uint16_t manager_ki, uint16_t manager_kd)
{
    kp = manager_kp; 
    ki = manager_ki; 
    kd = manager_kd;  
}

void MotorBase::getSyringeParams(uint16_t manager_diameter, uint16_t manager_lead, uint16_t manager_volume, uint16_t manager_syringe_flow)
{
    diameter = manager_diameter;
    lead = manager_lead;
    volume = manager_volume;
    syringe_flow = manager_syringe_flow;
}


void MotorBase::setSpeed(uint16_t speed)
{
     if(speed == 0)
    {
        speed_divide = 99999999;  // effectively stop
        return;
    }

    this->speed = speed;   

    last_speed_step_index = current_index;
    last_speed_step_time = micros();

    if(unit == 1)
    {
        speed_divide = (1000000.0f) / (speed * lut_index_size);    // 50 cycles is one rotation 
    }
    else if (unit == 2)
    {
        speed_divide = (1000000.0f) / (speed * lut_index_size * (num_step/4)); // rotations per second
    }

}

void MotorBase::updateInputs()
{
    if(sensorPin == 255) return;

    // Convert number, analog pin (e.g. 2 → A2)
    if(sensorPin == 254)
        sensorPin = 0;

    int pin = A0 + sensorPin;

    if(isAnalogSensor){
        analogValue = analogRead(sensorPin);
        
    } else {
        pinMode(sensorPin, INPUT_PULLUP);
        bool current_home = (digitalRead(pin) == LOW);

        indexTriggered = (current_home && !lastIndexState);
        lastIndexState = current_home;
    }


}

void MotorBase::update()
{
    if(isDisabled)
    {
        writeDAC(0, 0);   
        return;
    }

    if(!isRunning)
    {
        writeDAC(phaseA_output, phaseB_output);
        return;
    }

    updateInputs();

    if(currentMode)
        currentMode->update(*this);
    else
        step();
}

void MotorBase::step()
{

    long step = (micros() - last_speed_step_time) / speed_divide;

    current_index =
    (last_speed_step_index + direction * step) % lut_index_size;

    if(current_index < 0)
        current_index += lut_index_size;

    phaseA_output = output_scale*(cyc1_25ptable[current_index]);
    phaseB_output = output_scale*(cyc1_25ptable[current_index+200]);

    writeDAC(phaseA_output, phaseB_output);
}

void MotorBase::writeDAC(uint16_t valueA, uint16_t valueB)
{
#if USE_AD5689

    digitalWrite(csPin, LOW);
    SPI1.transfer(0b00111000);
    SPI1.transfer16(valueA);
    digitalWrite(csPin, HIGH);

    digitalWrite(csPin, LOW);
    SPI1.transfer(0b00110001);
    SPI1.transfer16(valueB);
    digitalWrite(csPin, HIGH);

    digitalWrite(_LDAC, LOW);
    digitalWrite(_LDAC, HIGH);

#else

    uint16_t dacA = 0x3000 | ((valueA >> 4) & 0x0FFF);
    uint16_t dacB = 0xB000 | ((valueB >> 4) & 0x0FFF);

    digitalWrite(csPin, LOW);
    SPI1.transfer16(dacA);
    digitalWrite(csPin, HIGH);

    digitalWrite(csPin, LOW);
    SPI1.transfer16(dacB);
    digitalWrite(csPin, HIGH);

    digitalWrite(_LDAC, LOW);
    digitalWrite(_LDAC, HIGH);

#endif
}