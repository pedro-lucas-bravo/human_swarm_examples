#define _USE_MATH_DEFINES

#include "Utils.h"
#include "Swarmalator.h"
#include "MusicalSwarmalator.h"
#include <cmath>
#include <random>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <iostream>

namespace {
    std::random_device rd;
    std::mt19937 gen(rd());
}

Swarmalator::Swarmalator(int id, bool isInteractive) :
    ID(id), J(1.0), K(-0.75), Position{ 0.0, 0.0, 0.0 }, PositionScale(10.0), Speed(4.0), Velocity{ 0.0, 0.0, 0.0 },
    Phase(0.0), Amplitude(1.0), Frequency(1.0), HueColor(0.0), oscillator(0.0), IsInteractive(isInteractive),MusicalSwarmalator(id)  {}

void Swarmalator::SetOthers(const std::vector<Swarmalator*>& others) {
    Others = others;
}

void Swarmalator::AssignRandomPosition(float radius) {
    std::uniform_real_distribution<> dis(-radius, radius);
    for (float& coord : Position) {
        coord = dis(gen);
    }
}

std::array<float, 3> Swarmalator::ScaledPosition() const {
    return { Position[0] * PositionScale, Position[1] * PositionScale, Position[2] * PositionScale };
}

std::array<float, 3> Swarmalator::ScaledVelocity() const {
	return { Velocity[0] * PositionScale, Velocity[1] * PositionScale, Velocity[2] * PositionScale };
}

void Swarmalator::SetFromScaledPosition(float x, float  y, float z) {
    Position[0] = x / PositionScale;
	Position[1] = y / PositionScale;
	Position[2] = z / PositionScale;
}

//reset oscillator by adjusting phase to start from zero
void Swarmalator::ResetOscillator(float current_time) {
	Phase = 2.0 * M_PI - std::fmod(2.0f * M_PI * Frequency * current_time, 2.0f * M_PI);
}

void Swarmalator::Update(float dt, float current_time) {
    if (!IsInteractive) {
        auto result = _delta_calculations();
        auto Xi = result.first;
        auto Oi = result.second;
        for (int i = 0; i < 3; ++i) {
            Velocity[i] = Xi[i] * Speed;
            Position[i] += Velocity[i] * dt;
        }
        Phase += Oi * Speed * dt;
        Phase = std::fmod(Phase, 2.0f * M_PI);
        if (Phase < 0) Phase += 2.0f * M_PI;
    }
    HueColor = Phase / (2.0f * M_PI);
    oscillator = Amplitude * std::sin(2 * M_PI * Frequency * current_time + Phase);
}

std::pair<std::array<float, 3>, float> Swarmalator::_delta_calculations() const {
    std::array<float, 3> Xi = { 0.0, 0.0, 0.0 };
    float Oi = 0.0;
    for (auto other : Others) {
        std::array<float, 3> Xji;
        for (int i = 0; i < 3; ++i) {
            Xji[i] = other->Position[i] - Position[i];
        }
        float Oji = other->Phase - Phase + std::uniform_real_distribution<>(0.0, 0.0001)(gen);
        float Xji_magnitude = vectorMagnitude(Xji[0], Xji[1], Xji[2]);
        for (int i = 0; i < 3; ++i) {
            Xi[i] += (Xji[i] / Xji_magnitude) * (1 + J * std::cos(Oji)) - (Xji[i] / std::pow(Xji_magnitude, 3));
        }
        Oi += std::sin(Oji) / Xji_magnitude;
    }
    int N = Others.size() + 1;
    for (float& xi : Xi) {
        xi /= N;
    }
    Oi *= (K / N);
    return { Xi, Oi };
}

std::string Swarmalator::CurrentColorHex() const {
    return calculate_color_hex(HueColor, oscillator, Amplitude);
}

std::array<float, 5> Swarmalator::calculate_params(float dt, float current_time, float myPhase, const std::array<float, 3>& myPosition,
    const std::vector<float>& othersPhases, const std::vector<std::array<float, 3>>& othersPositions,
    float J, float K, float speed, float amplitude, float frequency) {
    std::array<float, 3> Xi = { 0.0, 0.0, 0.0 };
    float Oi = 0.0;
    int num_others = othersPhases.size();
    for (int j = 0; j < num_others; ++j) {
        std::array<float, 3> Xji;
        for (int i = 0; i < 3; ++i) {
            Xji[i] = othersPositions[j][i] - myPosition[i];
        }
        float Oji = othersPhases[j] - myPhase + std::uniform_real_distribution<>(0.0, 0.0001)(gen);
        float Xji_magnitude = vectorMagnitude(Xji[0], Xji[1], Xji[2]);
        for (int i = 0; i < 3; ++i) {
            Xi[i] += (Xji[i] / Xji_magnitude) * (1 + J * std::cos(Oji)) - (Xji[i] / std::pow(Xji_magnitude, 3));
        }
        Oi += std::sin(Oji) / Xji_magnitude;
    }
    int N = num_others + 1;
    for (float& xi : Xi) {
        xi /= N;
    }
    Oi *= (K / N);

    float pi2 = 2 * M_PI;
    std::array<float, 3> myNewPosition;
    for (int i = 0; i < 3; ++i) {
        myNewPosition[i] = myPosition[i] + Xi[i] * speed * dt;
    }
    float myNewPhase = std::fmod(myPhase + Oi * speed * dt, pi2);
    if (myNewPhase < 0) myNewPhase += pi2;
    float hueColor = myNewPhase / pi2;
    float oscillator = amplitude * std::sin(pi2 * frequency * current_time + myNewPhase);

    return { myNewPosition[0], myNewPosition[1], myNewPosition[2], hueColor, oscillator };
}

std::string Swarmalator::calculate_color_hex(float hueColor, float oscillator, float amplitude) {
    auto hsv_to_rgb = [](float h, float s, float v) {
        float r, g, b;
        int i = static_cast<int>(h * 6);
        float f = h * 6 - i;
        float p = v * (1 - s);
        float q = v * (1 - f * s);
        float t = v * (1 - (1 - f) * s);

        switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
        }
        return std::array<float, 3> {r, g, b};
        };

    std::array<float, 3> target_color = hsv_to_rgb(hueColor, 1.0f, 1.0f);
    std::array<float, 3> neutral_color = { 0.0f, 0.0f, 0.0f };
    std::array<float, 3> current_color;
    for (int i = 0; i < 3; ++i) {
        current_color[i] = neutral_color[i] + (target_color[i] - neutral_color[i]) * (oscillator + amplitude) / (2 * amplitude);
    }

    std::ostringstream oss;
    oss << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(current_color[0] * 255)
        << std::setw(2) << static_cast<int>(current_color[1] * 255)
        << std::setw(2) << static_cast<int>(current_color[2] * 255);
    return oss.str();
}
