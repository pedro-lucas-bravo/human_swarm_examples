
import math
import numpy as np
import random
import colorsys
import MusicalSwarmalator

class Swarmalator:
    def __init__(self, id, isInteractive):
        self.ID = id
        self.J = 1.0#0.1
        self.K = -0.75#1.0
        self.Position = np.array([0.0,0.0,0.0])
        self.Velocity = np.array([0.0,0.0,0.0])
        self.PositionScale = 10.0
        self.Speed = 4.0
        self.Phase = 0.0
        self.Amplitude = 1.0
        self.Frequency = 1.0
        self.HueColor = 0.0
        self.oscillator = 0
        self.Others = []
        self.isInteractive = isInteractive
        if not isInteractive:
            self.MusicalAgent = MusicalSwarmalator.MusicalSwarmalator(self.ID)

    def SetOthers(self, others):
        self.Others= others

    def AssignRandomPosition(self, radius):
        self.Position = np.array([random.uniform(-radius, radius), random.uniform(-radius, radius), random.uniform(-radius, radius)])

    def ScaledPosition(self):
        return self.Position * self.PositionScale
    
    def ScaledVelocity(self):
        return self.Velocity * self.PositionScale
    
    def SetFromScalePosition(self, x, y, z):
        self.Position = np.array([x, y, z]) / self.PositionScale

    #reset oscillator by adjusting phase to start from zero
    def ResetOscillator(self, current_time):
        self.Phase = 2 * math.pi - ((2.0*math.pi * self.Frequency * current_time) % (2.0*math.pi))        


    #Time is in seconds
    def Update(self, dt, current_time):
        if not self.isInteractive:        
            (Xi, Oi) = self._delta_calculations()     
            self.Velocity = Xi * self.Speed
            self.Position += self.Velocity * dt            
            self.Phase += Oi * self.Speed * dt
            self.Phase = self.Phase % (2 * math.pi)
            self.Phase = self.Phase + (2 * math.pi) if self.Phase < 0 else self.Phase
        self.HueColor = (self.Phase / (2 * math.pi))
        self.oscillator = self.Amplitude * math.sin(2 * math.pi * self.Frequency * current_time + self.Phase)

    def _delta_calculations(self):
        Xi = np.array([0.0,0.0,0.0])
        Oi = 0
        for j in range(len(self.Others)):
            Xji = self.Others[j].Position - self.Position
            Oji = self.Others[j].Phase - self.Phase + random.uniform(0, 0.0001)
            Xji_magnitude = np.linalg.norm(Xji)            
            Xi += (Xji / Xji_magnitude) * (1 + self.J * math.cos(Oji)) - Xji / math.pow(Xji_magnitude, 3)
            Oi += math.sin(Oji) / Xji_magnitude
        N = len(self.Others) + 1  # +1 because agents does not contain "this" agent
        Xi /= N
        Oi *= (self.K / N)
        return (Xi, Oi)
    
    def CurrentColorHex(self):
        return Swarmalator.calculate_color_hex(self.HueColor, self.oscillator, self.Amplitude)
    
    #This logic is duplicated from the Update method and _delta_calculations method
    #TODO: Refactor to avoid code duplication if performance is not affected
    @staticmethod
    def calculate_params(dt, current_time, myPhase, myPosition, othersPhases, othersPositions, J, K, speed, amplitude, frequency):
        # Delta calculations
        Xi = np.zeros(3)
        Oi = 0
        num_others = len(othersPhases)  # it is assumed that othersPhases and othersPositions have the same length
        for j in range(num_others):
            Xji = othersPositions[j] - myPosition
            Oji = othersPhases[j] - myPhase + random.uniform(0, 0.0001)
            Xji_magnitude = np.linalg.norm(Xji)
            Xi += (Xji / Xji_magnitude) * (1 + J * math.cos(Oji)) - Xji / (Xji_magnitude ** 3)
            Oi += math.sin(Oji) / Xji_magnitude
        N = num_others + 1  # +1 because agents does not contain "this" agent
        Xi /= N
        Oi *= (K / N)

        #Parameter calculations
        pi2 = 2 * math.pi
        myNewVelocity = Xi * speed
        myNewPosition = myPosition + myNewVelocity * dt
        myNewPhase = (myPhase + Oi * speed * dt) % pi2
        myNewPhase = myNewPhase + pi2 if myNewPhase < 0 else myNewPhase
        hueColor = myNewPhase / pi2
        oscillator = amplitude * math.sin(pi2 * frequency * current_time + myNewPhase)

        return [myNewPosition, myNewVelocity, myNewPhase, hueColor, oscillator, Swarmalator.calculate_color_hex(hueColor, oscillator, amplitude)]
    
    @staticmethod
    def calculate_color_hex(hueColor, oscillator, amplitude):
        #Update color
        target_color = colorsys.hsv_to_rgb(hueColor, 1, 1)
        neutral_color = (0.0, 0.0, 0.0)  # black
        current_color = tuple(neutral_color[i] + (target_color[i] - neutral_color[i]) * (oscillator + amplitude) / (2 * amplitude) for i in range(3))
        return '%02x%02x%02x' % tuple(int(c * 255) for c in current_color)


