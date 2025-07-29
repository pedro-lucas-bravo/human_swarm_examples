import Utils
import numpy as np
import MusicalAgent

class Agent:
    def __init__(self, id, init_position, speed, limit_radius, type):#Units: mm for distance and mm/s for speed
        self.id = id
        self.position = np.array(init_position)
        self.speed = speed
        self.limit_radius = limit_radius
        #Fill dir with the normalized vector of the initial position
        self.dir = self.position / np.linalg.norm(self.position) if np.linalg.norm(self.position) > 0 else np.array([1.0, 0.0, 0.0])
        self.speed_factor = 1.0
        self.type = type  # Type of agent, e.g., '0:sphere and automous', '1:cube and user controlled', etc.
        self.MusicalAgent = MusicalAgent.MusicalAgent(self.id)

    def detect_limit(self):
        return np.linalg.norm(self.position) > self.limit_radius

    def update(self, delta_time_ms):   
        delta_time_s = delta_time_ms / 1000.0
        if self.type == 0:
            # if limit is found, bounce a random angle
            if self.detect_limit():
                random_direction = np.array(Utils.random_position_within_radius(1, constant_radius=True))
                # Angle between the current position (normal to collision) and the new random direction
                angle = np.arccos(np.dot(self.position, random_direction) / (np.linalg.norm(self.position) * np.linalg.norm(random_direction)))
                # Reflect the direction vector if the angle is less than 90 degrees
                random_direction = -random_direction if angle < np.pi / 2 else random_direction
                self.dir = random_direction

            # Update the agent's position based on its speed and delta_time
            self.position += self.dir * self.speed * self.speed_factor * delta_time_s

    def set_speed_factor(self, speed_factor):
        self.speed_factor = speed_factor



