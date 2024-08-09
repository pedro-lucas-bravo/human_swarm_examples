from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

class MusicalAgent:
    def __init__(self, id):
        self.id = id
        self.currentNoteDuration = 0
        self.noteTimer = 0
        self.playingNote = False
        self.SendNoteOff = False

    def update(self, deltaTimeMs):
        self.SendNoteOff = False
        if self.playingNote:
            self.noteTimer += deltaTimeMs
            if self.noteTimer >= self.currentNoteDuration:
                self.playingNote = False
                self.noteTimer = 0
                self.SendNoteOff = True


    def InstantiationBundle(self, oscType, attack, decay, sustain, release):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle.add_content(self.OSC_MSG_InstantiateExternal())
        bundle.add_content(self.OSC_MSG_SetOscillator(oscType))
        bundle.add_content(self.OSC_MSG_ADSR(attack, decay, sustain, release))
        bundle.add_content(self.OSC_MSG_SetGain(0.5))
        return bundle.build()

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

    def OSC_MSG_MidiNote(self, note, velocity, durationMs):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/note")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(note)
        osc_msg.add_arg(velocity)
        if velocity > 0:
            self.playingNote = True
            self.currentNoteDuration = durationMs
            self.noteTimer = 0
        return osc_msg.build()

    def OSC_MSG_SetFrequency(self, frequency):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(2) #2 is frequency
        osc_msg.add_arg(frequency)
        return osc_msg.build()

    def OSC_MSG_SetGain(self, gain):
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(16) #16 is gain
        osc_msg.add_arg(gain)
        return osc_msg.build()

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
    
    def OSC_MSG_MAP_Sound_MovementDynamics(self, angleDegress, angularSpeedFactor, actualRadius, lastCloserAtttactorIdx):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        ####### Frequency mapping #######

        #angleDegress [0,360] to [-1, 1]
        angleDegressFactor = (angleDegress - 180) / 180
        absAnglesDegressFactor = abs(angleDegressFactor)   
        frequencyBase = 300 + absAnglesDegressFactor * 1700 #Freq from 300 to 2000        
        
        #Angular speed [-1.5, 1.5] to [-2, 2]
        angularSpeed = -2 + ((angularSpeedFactor + 1.5) / 3) * 4
        absAngularSpeed = abs(angularSpeed) + 0.1

        #Radius mapping [5000, 10000] to [1, 4]
        radius = (actualRadius - 5000) / (10000 - 5000) * (4 - 1) + 1
        radius = max(1, min(radius, 4))

        totalFrequency = frequencyBase * absAngularSpeed * radius

        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(2) #2 is frequency
        osc_msg.add_arg(totalFrequency)
        bundle.add_content(osc_msg.build())

        ####### LPF mapping #######
        #Radius mapping [5000, 10000] to [22000, 300]
        radiusLpf = (actualRadius - 5000) / (10000 - 5000) * (300 - 22000) + 22000
        cuttOffFreqLpf = max(300, min(radiusLpf, 22000))
        resonance = 0.9

        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(93) #93 is LPF cutoff
        osc_msg.add_arg(cuttOffFreqLpf)
        bundle.add_content(osc_msg.build())

        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(18) #18 is LPF Q
        osc_msg.add_arg(resonance)
        bundle.add_content(osc_msg.build())

        ###### Reverb mapping ######
        #Radius mapping [7000, 10000] to [-10000, 0]
        radiusReverb = (actualRadius - 7000) / (10000 - 7000) * (0 - (-10000)) + (-10000)
        radiusReverb = max(-10000, min(radiusReverb, 0))

        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/audio/synth/param_val")
        osc_msg.add_arg(self.id)
        osc_msg.add_arg(0)
        osc_msg.add_arg(19) #19 is Reverb room
        osc_msg.add_arg(radiusReverb)
        bundle.add_content(osc_msg.build())

        ###### Oscillator mapping ######
        if lastCloserAtttactorIdx != -1:
            oscillatorType = 1 if lastCloserAtttactorIdx == 1000 else 3
            osc_msg = self.OSC_MSG_SetOscillator(oscillatorType)
            bundle.add_content(osc_msg)
              

        return bundle.build()
    
    def CalculateNoteLengthFromAngularSpeed(self, angularSpeedFactor):
        #Angular speed [-1.5, 1.5] to [-4800, 4800]
        angularSpeed = -4800 + ((angularSpeedFactor + 1.5) / 3) * 9600
        return abs(angularSpeed) + 200 #in ms
    
