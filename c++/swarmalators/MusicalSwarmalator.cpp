#include "Utils.h"
#include "MusicalSwarmalator.h"
#include <cmath>
#include <array>

#include <osc/OscOutboundPacketStream.h>

MusicalSwarmalator::MusicalSwarmalator(int id):
    ID(id), baseGain(0.5) {}

std::pair<float, float> MusicalSwarmalator::GetSoundMapping(float swarmalator_phase, float swarmalator_amplitude, const std::array<float, 3>& swarmalator_scaled_velocity) {
    const float min_freq = 200.0f;
    const float max_freq = 2000.0f;

    float sound_frequency = min_freq + (max_freq - min_freq) * sin(swarmalator_phase * 0.5f);

    float mod_amplitude = baseGain * (swarmalator_amplitude + 1.0f) * 0.5f;

    const float scale_factor = 5.0f;
    float velocity_magnitude = vectorMagnitude(swarmalator_scaled_velocity[0], swarmalator_scaled_velocity[1], swarmalator_scaled_velocity[2]);
    velocity_magnitude = pow(velocity_magnitude, 2);
    sound_frequency += scale_factor * velocity_magnitude;

    return { sound_frequency, mod_amplitude };
}

void MusicalSwarmalator::InstantiateBundleAndPlay(osc::OutboundPacketStream& bundle, int oscType, float attack, float decay, float sustain, float release, float init_swarmalator_phase, float init_swarmalator_amplitude, const std::array<float, 3>& init_swarmalator_scaled_velocity) {
	OSC_MSG_InstantiateExternal(bundle);
	OSC_MSG_SetOscillator(bundle, oscType);
	OSC_MSG_ADSR(bundle, attack, decay, sustain, release);
	baseGain = 0.5;
	OSC_MSG_MidiNote(bundle, 0, 127);
	UpdateBundle(bundle, init_swarmalator_phase, init_swarmalator_amplitude, init_swarmalator_scaled_velocity);
}

void MusicalSwarmalator::UpdateBundle(osc::OutboundPacketStream& bundle, float swarmalator_phase, float swarmalator_amplitude, const std::array<float, 3>& init_swarmalator_scaled_velocity) {
	auto sound_mappings = GetSoundMapping(swarmalator_phase, swarmalator_amplitude, init_swarmalator_scaled_velocity);
	float sound_frequency = sound_mappings.first;
	float mod_amplitude = sound_mappings.second;

	OSC_MSG_SetFrequency(bundle, sound_frequency);
	OSC_MSG_SetGain(bundle, mod_amplitude);
}

void MusicalSwarmalator::OSC_MSG_InstantiateExternal(osc::OutboundPacketStream& bundle) {
    bundle << osc::BeginMessage("/agents/audio/synth/add/id");
    bundle << ID;
    bundle << osc::EndMessage;
}

void MusicalSwarmalator::OSC_MSG_SetOscillator(osc::OutboundPacketStream& bundle, int oscType) {
    bundle << osc::BeginMessage("/agents/audio/synth/param_val");
    bundle << ID;
    bundle << 0;
    bundle << 1; // 1 is oscillator type
    bundle << oscType;
    bundle << osc::EndMessage;
}

void MusicalSwarmalator::OSC_MSG_MidiNote(osc::OutboundPacketStream& bundle, int note, int velocity) {
	bundle << osc::BeginMessage("/agents/audio/synth/note");
	bundle << ID;
    bundle << 0;
	bundle << note;
	bundle << velocity;
	bundle << osc::EndMessage;
}

void MusicalSwarmalator::OSC_MSG_SetFrequency(osc::OutboundPacketStream& bundle, float frequency) {
	bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 2; // 2 is frequency
	bundle << frequency;
	bundle << osc::EndMessage;
}

void MusicalSwarmalator::OSC_MSG_SetGain(osc::OutboundPacketStream& bundle, float gain) {
	bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 16; // 16 is gain
	bundle << gain;
	bundle << osc::EndMessage;
}

void MusicalSwarmalator::OSC_MSG_ADSR(osc::OutboundPacketStream& bundle, float attack, float decay, float sustain, float release) {
    bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 82; // 82 is attack
	bundle << attack;
	bundle << osc::EndMessage;

	bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 83; // 83 is decay
	bundle << decay;
	bundle << osc::EndMessage;

	bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 85; // 85 is sustain
	bundle << sustain;
	bundle << osc::EndMessage;

	bundle << osc::BeginMessage("/agents/audio/synth/param_val");
	bundle << ID;
	bundle << 0;
	bundle << 17; // 17 is release
	bundle << release;
	bundle << osc::EndMessage;
}

