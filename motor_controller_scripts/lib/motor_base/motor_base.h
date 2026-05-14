#pragma once

#include <Arduino.h>

class MotorMode;

class MotorBase {
public:
    MotorBase();

    void init(uint8_t cs, uint16_t speed);

    void start(uint16_t speed_start);
    void stop();
    void disable();
    void reverse(int num);
    void setSpeed(uint16_t speed);

    void update();
    void setUnit(uint8_t speed_unit);
    void step();

    void setMode(MotorMode* m);
    void setSensorPin(uint8_t pin);
    void startHoming();
    void getTankLevel(uint16_t manager_tank_level);

    void getStepLimit(uint8_t manager_step_limit);
    void getFlowRate(uint8_t manager_flow_rate);
    void getPID(uint16_t manager_kp, uint16_t manager_ki, uint16_t manager_kd);
    void getSyringeParams(uint16_t manager_diameter, uint16_t manager_lead, uint16_t manager_volume, uint16_t manager_syringe_flow);



    uint8_t getCSPin();

    // shared state
    bool indexTriggered;
    const int lut_index_size = 800;
    int direction;
    long current_index;
    bool currenr_home;
    bool currentState = false;

    // change this to private again once the testing has been done
    uint16_t phaseA_output;
    uint16_t phaseB_output;
    MotorMode* currentMode;

    unsigned long last_speed_step_time;
    long last_speed_step_index;
    int unit;
    uint8_t csPin;
    uint16_t speed;
    uint16_t target_tank_level;
    uint8_t step_limit; 
    uint8_t flow_rate;
    uint16_t kp;
    uint16_t ki;
    uint16_t kd;
    uint16_t diameter;
    uint16_t lead;
    uint16_t volume;
    uint16_t syringe_flow;

    bool isAnalogSensor = false;
    int analogValue = 0;

    bool isHoming;
    long position;
    int num_step;

private:
    

    bool isRunning;
    

    long phase;
    uint16_t speed_divide;

    // uint16_t phaseA_output;
    // uint16_t phaseB_output;

    long rpm;
    
    // mode system
   
    const int output_scale = 32768/2048;
    

    // sensor
    uint8_t sensorPin;
    bool lastIndexState;

    void updateInputs();
    void writeDAC(uint16_t valueA, uint16_t valueB);

    bool isDisabled = false;
};