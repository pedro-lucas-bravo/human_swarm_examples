#include "Utils.h"
#include <cmath>

float vectorMagnitude(float x, float y, float z) {
    float sum = x * x + y * y + z * z;
    return std::sqrt(sum);
}