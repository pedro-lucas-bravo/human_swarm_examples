from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import numpy as np

class MusicalAgent:
    def __init__(self, id):
        self.id = id
        self.BaseFrequency = 440.0  # A4

    ############# START: Setup variables for note playing #############

    def InstantiationBundle(self, oscType):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle.add_content(self.OSC_MSG_InstantiateExternal().build())
        bundle.add_content(self.OSC_MSG_SetOscillator(oscType).build())
        bundle.add_content(self.OSC_MSG_SetGain(0.5).build())
        return bundle
    
    def PlayMsg(self):
        note = 0 #Placeholder for note
        velocity = 127 #Note on
        return self.OSC_MSG_MidiNote(note, velocity)
    
    def StopMsg(self):
        note = 0
        velocity = 0 #Note off
        return self.OSC_MSG_MidiNote(note, velocity)
    
    def update(self, limit_radius, spatial_position):
        # Sound Mapping: Calculate frequency based on distance from origin
        magnitude = np.linalg.norm(spatial_position)
        return self.OSC_MSG_SetFrequency(self.BaseFrequency * (magnitude / limit_radius))
    
    ############## END: Setup variables for note playing #############


    ################# START: OSC Messages for Musical Agent #############


    def OSC_MSG_InstantiateExternal(self):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/add/id")
        osc_msg.add_arg(self.id)
        return osc_msg
    
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
        return osc_msg

    def OSC_MSG_SetFrequency(self, frequency):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(2) #2 is frequency
        osc_msg.add_arg(frequency)
        return osc_msg

    def OSC_MSG_SetGain(self, gain):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(16) #16 is gain
        osc_msg.add_arg(gain)
        return osc_msg
    
    def OSC_MSG_MidiNote(self, note, velocity):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/note")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(note)
        osc_msg.add_arg(velocity)
        return osc_msg
    
    ############### END: OSC Messages for Musical Agent #############