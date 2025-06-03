import random
import math

def random_position_within_radius(radius, constant_radius=False):   
        az = random.uniform(0, math.pi * 2)
        elv = random.uniform(0, math.pi)
        if constant_radius:
           r = radius
        else:
           r = random.uniform(0, radius)
        x = r * math.sin(elv) * math.cos(az)
        y = r * math.sin(elv) * math.sin(az)
        z = r * math.cos(elv)
        return [x, y, z]

def is_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False