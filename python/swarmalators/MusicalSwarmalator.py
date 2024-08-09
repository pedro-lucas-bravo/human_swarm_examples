import math
import numpy as np

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

class MusicalSwarmalator:
    def __init__(self, id):
        self.id = id
        self.baseGain = 0.5

    def _GetSoundMapping(self, swarmalator_phase, swarmalator_amplitude, swarmalator_scaled_velocity):
        #frequency mapping from swarmalator phase [0, 2*pi] to [200, 2000, 200] being PI the center
        min_freq = 200
        max_freq = 2000
        sound_frequency = min_freq + (max_freq - min_freq) * math.sin(swarmalator_phase * 0.5)

        #amplitude mapping from amplitude [-1, 1] to [0, 1] according to gain
        mod_amplitude = self.baseGain * (swarmalator_amplitude + 1) * 0.5

        #Boost the sound_frequency according to velocity magnitude
        scale_factor = 5.0
        velocity_magnitude = np.linalg.norm(swarmalator_scaled_velocity)
        # Shape the velocity magnitude to be more sensitive to small values
        velocity_magnitude = velocity_magnitude ** 2
        # increase with exponential
        sound_frequency += scale_factor * velocity_magnitude


        #LPF cut off mapping from scaled position magnitude [0, 20] to [22000, 300]
        # min_radius = 0
        # max_radius = 20
        # min_lpf_freq = 10000
        # max_lpf_freq = 300
        # magnitude = np.linalg.norm(swarmalator_scaled_position)
        # limited_magnitude = max(min_radius, min(max_radius, magnitude))
        # lpf_frequency = min_lpf_freq + (max_lpf_freq - min_lpf_freq) * (limited_magnitude - min_radius) / (max_radius - min_radius)

        return (sound_frequency, mod_amplitude)

    # Instantiate AFTER the agent has been created
    def InstantiationBundle_and_Play(self, oscType, attack, decay, sustain, release, init_swarmalator_phase, init_swarmalator_amplitude, init_swarmalator_scaled_velocity):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle.add_content(self.OSC_MSG_InstantiateExternal())
        bundle.add_content(self.OSC_MSG_SetOscillator(oscType))
        bundle.add_content(self.OSC_MSG_ADSR(attack, decay, sustain, release))
        self.baseGain = 0.5
        bundle.add_content(self.OSC_MSG_MidiNote(0, 127)) #init play
        bundle.add_content(self.UpdateBundle(init_swarmalator_phase, init_swarmalator_amplitude, init_swarmalator_scaled_velocity))
        return bundle.build()
    
    
    def OSC_MSG_StopSound(self):
        return self.OSC_MSG_MidiNote(0, 0)
    
    def UpdateBundle(self, swarmalator_phase, swarmalator_amplitude, swarmalator_scaled_velocity):
        #Get mapping
        sound_frequency, mod_amplitude = self._GetSoundMapping(swarmalator_phase, swarmalator_amplitude, swarmalator_scaled_velocity)

        #Create bundle
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle.add_content(self.OSC_MSG_SetFrequency(sound_frequency))
        bundle.add_content(self.OSC_MSG_SetGain(mod_amplitude))
        #bundle.add_content(self.OSC_MSG_LPF_Freq(lpf_freq))
        #bundle.add_content(self.OSC_MSG_LPF_Resonance(0.9))
        return bundle.build()
    
    #################### Elemental music OSC messages ####################

    # Add the audio component to an existing agent
    def OSC_MSG_InstantiateExternal(self):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/add/id")
        osc_msg.add_arg(self.id)
        return osc_msg.build()


    # Sine = 0,
    # Square = 1,
    # Saw = 2,
    # Triangle = 3
    def OSC_MSG_SetOscillator(self, oscType):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val") # id, bank, param_id, value
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(1) #1 is oscillator type
        osc_msg.add_arg(oscType)
        return osc_msg.build()


    # if velocity is diffrent than 0, it will play the note, otherwise it will stop it
    def OSC_MSG_MidiNote(self, note, velocity):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/note")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(note)
        osc_msg.add_arg(velocity)
        return osc_msg.build()

    # Set the frequency of the oscillator
    def OSC_MSG_SetFrequency(self, frequency):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(2) #2 is frequency
        osc_msg.add_arg(frequency)
        return osc_msg.build()

    # Set the gain of the oscillator
    def OSC_MSG_SetGain(self, gain):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(16) #16 is gain
        osc_msg.add_arg(gain)
        return osc_msg.build()

    # Set the ADSR of the oscillator
    def OSC_MSG_ADSR(self, attack, decay, sustain, release):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        #Attack
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(82) #82 is attack
        osc_msg.add_arg(attack)
        bundle.add_content(osc_msg.build())
        #Decay
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(83) #83 is decay
        osc_msg.add_arg(decay)
        bundle.add_content(osc_msg.build())
        #Sustain
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(85) #85 is sustain
        osc_msg.add_arg(sustain)
        bundle.add_content(osc_msg.build())
        #Release
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(17) #17 is release
        osc_msg.add_arg(release)
        bundle.add_content(osc_msg.build())

        return bundle.build()
    
    def OSC_MSG_LPF_Freq(self, cuttOffFreqLpf):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(93) #93 is LPF cutoff
        osc_msg.add_arg(cuttOffFreqLpf)
        return osc_msg.build()
    
    def OSC_MSG_LPF_Resonance(self, resonance):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(18) #18 is LPF Q
        osc_msg.add_arg(resonance)
        return osc_msg.build()