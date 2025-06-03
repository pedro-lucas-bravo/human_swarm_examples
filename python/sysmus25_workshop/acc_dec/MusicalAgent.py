from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import numpy as np

class MusicalAgent:
    def __init__(self, id):
        self.id = id
        self.BaseFrequency = 440.0  # A4

        #Scales to chhoose from
        self.scales = [
            #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # ChromaticScale
            #[0, 3, 5, 6, 7, 10],                     # MinorBluesScale
            [0, 2, 4, 5, 6, 9],                      # MajorBluesScale
            [0, 2, 4, 5, 7, 9, 11],                  # MajorScale
            #[0, 2, 3, 5, 7, 8, 10],                  # MinorScale
            [0, 2, 4, 7, 9],                         # MajorPentatonic
            [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]   # FifthSequence
        ]
        self.scale = self.scales[np.random.randint(len(self.scales))]
        self.octavesRange = np.random.randint(1, 4)  # Randomly choose between 1 and 3 octaves
        # Expanding the scale to cover the octaves. 
        # Example: if scale is [0, 2, 4] and octavesRange is 2, the scale will be [0, 2, 4, 12, 14, 16]
        self.scale = [note + 12 * octave for octave in range(self.octavesRange) for note in self.scale]
        self.BaseMidiNote = 60 - 12  # C3 (60 - 12) in MIDI note numbers
        self._lastNote = None  # To keep track of the last note played  


    ############# START: Setup variables for note playing #############

    def InstantiationBundle(self, oscType):
        self.type = oscType  # Type of oscillator
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle.add_content(self.OSC_MSG_InstantiateExternal().build())
        bundle.add_content(self.OSC_MSG_SetOscillator(oscType).build())
        bundle.add_content(self.OSC_MSG_SetGain(0.5 if oscType == 0 else 0.2).build())
        bundle.add_content(self.OSC_MSG_ADSR(0.01, 0.1, 0.8, 1.0).build())
        return bundle
    
    def update(self, limit_radius, spatial_position, velocity, nearby_agents):   
        #Velocity is mapped to reverb factor
        speed = np.linalg.norm(velocity)
        speed_tuning = 2000 if self.type == 0 else 5000
        reverb_factor = np.clip(speed / speed_tuning, 0, 1)

        #If there is any nearby agent, set the frequency, otherwise set zero frequency
        if len(nearby_agents) == 0:
            if self._lastNote is not None: 
                last_note = self._lastNote
                self._lastNote = None
                return self.OSC_MSG_MidiNote(self.BaseMidiNote + self.scale[last_note], 0)
            return None
        else:
            # Sound Mapping: Calculate note based on distance from origin
            magnitude = np.linalg.norm(spatial_position)
            # Chose note depending on the distance from the origin
            note_index = int(np.clip((magnitude / limit_radius) * len(self.scale), 0, len(self.scale) - 1))            
            if self._lastNote is not None:                
                if note_index != self._lastNote:
                    mapping_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
                    mapping_bundle.add_content(self.OSC_MSG_MidiNote(self.BaseMidiNote + self.scale[self._lastNote], 0).build()) # Note off the last note
                    mapping_bundle.add_content(self.OSC_MSG_MidiNote(self.BaseMidiNote + self.scale[note_index], 127).build())  # Note on the new note                    
                    mapping_bundle.add_content(self.OSC_MSG_Reverb(reverb_factor).build())
                    self._lastNote = note_index
                    return mapping_bundle
                else:
                    return None
            else:
                self._lastNote = note_index
                mapping_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
                mapping_bundle.add_content(self.OSC_MSG_MidiNote(self.BaseMidiNote + self.scale[note_index], 127).build())
                mapping_bundle.add_content(self.OSC_MSG_Reverb(reverb_factor).build())
                return mapping_bundle
    
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
    
    def OSC_MSG_Flush(self):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/flush")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        return osc_msg
    
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
        return bundle
    
    def OSC_MSG_Reverb(self, factor):
        #mapping [0, 1] to [-10000, 0]
        reverbRoom = -10000 + factor * 10000
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(19) #19 is Reverb room
        osc_msg.add_arg(reverbRoom)
        return osc_msg
    
    ############### END: OSC Messages for Musical Agent #############