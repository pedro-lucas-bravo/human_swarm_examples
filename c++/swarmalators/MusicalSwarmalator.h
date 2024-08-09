#ifndef MUSICAL_SWARMALATOR_H
#define MUSICAL_SWARMALATOR_H

#include <vector>
#include <osc/OscOutboundPacketStream.h>

class MusicalSwarmalator {
public:
	int ID;
	MusicalSwarmalator(int id);
	void InstantiateBundleAndPlay(osc::OutboundPacketStream& bundle, int oscType, float attack, float decay, float sustain, float release, float init_swarmalator_phase, float init_swarmalator_amplitude, const std::array<float, 3>& init_swarmalator_scaled_velocity);
	void UpdateBundle(osc::OutboundPacketStream& bundle, float swarmalator_phase, float swarmalator_amplitude, const std::array<float, 3>& init_swarmalator_scaled_velocity);
private:
	float baseGain;
	std::pair<float, float> GetSoundMapping(float swarmalator_phase, float swarmalator_amplitude, const std::array<float, 3>& swarmalator_scaled_velocity);
	void OSC_MSG_InstantiateExternal(osc::OutboundPacketStream& bundle);
	void OSC_MSG_SetOscillator(osc::OutboundPacketStream& bundle, int oscType);
	void OSC_MSG_MidiNote(osc::OutboundPacketStream& bundle, int note, int velocity);
	void OSC_MSG_SetFrequency(osc::OutboundPacketStream& bundle, float frequency);
	void OSC_MSG_SetGain(osc::OutboundPacketStream& bundle, float gain);
	void OSC_MSG_ADSR(osc::OutboundPacketStream& bundle, float attack, float decay, float sustain, float release);
};

#endif // MUSICAL_SWARMALATOR_H