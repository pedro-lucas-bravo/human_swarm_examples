#ifndef SWARMALATOR_H
#define SWARMALATOR_H

#include "MusicalSwarmalator.h"
#include <vector>
#include <array>
#include <string>

class Swarmalator {
public:
    int ID;
    float J;
    float K;
    float Speed;

    float Phase;
    float oscillator;
    bool IsInteractive;
    MusicalSwarmalator MusicalSwarmalator;

    Swarmalator(int id, bool isInteractive);
        
    void SetOthers(const std::vector<Swarmalator*>& others);
    void AssignRandomPosition(float radius);
    std::array<float, 3> ScaledPosition() const;
    std::array<float, 3> ScaledVelocity() const;
    void SetFromScaledPosition(float x, float  y, float z);
    void ResetOscillator(float current_time);
    void Update(float dt, float current_time);
    std::string CurrentColorHex() const;

    static std::array<float, 5> calculate_params(float dt, float current_time, float myPhase, const std::array<float, 3>& myPosition,
        const std::vector<float>& othersPhases, const std::vector<std::array<float, 3>>& othersPositions,
        float J, float K, float speed, float amplitude, float frequency);

    static std::string calculate_color_hex(float hueColor, float oscillator, float amplitude);

private:
    std::pair<std::array<float, 3>, float> _delta_calculations() const;    
    std::array<float, 3> Position;
    std::array<float, 3> Velocity;
    float PositionScale;   

    float Amplitude;
    float Frequency;
    float HueColor;    
    std::vector<Swarmalator*> Others;
};

#endif // SWARMALATOR_H

