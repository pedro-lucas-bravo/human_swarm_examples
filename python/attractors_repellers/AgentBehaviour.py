import math
import random
import colorsys
import MusicalAgent

class AgentBehaviour:
    def __init__(self, id):
        self.id = id
        self.center = {'x': 0, 'y': 0, 'z': 0}
        self.movingPoint = {'x': 0, 'y': 0, 'z': 0}
        self.axis = {'x': 0, 'y': 0, 'z': 1}
        self.w_speed = 2 * math.pi * 0.1  # Angular speed (radians per second)
        self.currentAngle = 0
        self.initialAngle = 0
        self.currentRadious = 5000
        self.attractors = [{'id': -1, 'radius': 5000, 'x': 0, 'y': 0, 'z': 0} for _ in range(10)]
        self.repellers = [{'id': -1, 'radius': 10000, 'x': 0, 'y': 0, 'z': 0} for _ in range(10)]
        self.lastCloserAttractorIdx = -1
        self.colorHex = "00e5ff"
        self.localCommPeriodMs = 500        
        self.localCommTimerMs =  random.randint(0, self.localCommPeriodMs)
        self.send_local_msg = False
        self.local_message = None
        self.MusicalAgent = MusicalAgent.MusicalAgent(self.id)
        self.playbackPeriodMs = 1000
        self.playbackTimerMs = random.randint(0, self.playbackPeriodMs)
        self.playbackTimer_expired = False

        self.axis_random()
        self.angle_random()

    def _cross_product(self, v1, v2):
        return {'x': v1['y']*v2['z'] - v1['z']*v2['y'],
                'y': v1['z']*v2['x'] - v1['x']*v2['z'],
                'z': v1['x']*v2['y'] - v1['y']*v2['x']}

    def _magnitude_vect(self, v):
        return math.sqrt(v['x']**2 + v['y']**2 + v['z']**2)

    def _normalize(self, v):
        magnitude = self._magnitude_vect(v)
        return {'x': v['x'] / magnitude, 'y': v['y'] / magnitude, 'z': v['z'] / magnitude}

    def _rotate(self, radius, center, axis, angle):
        up_vector = {'x': 0, 'y': 1, 'z': 0}
        plane_vector_a = self._cross_product(up_vector, axis)
        plane_vector_b = self._cross_product(axis, plane_vector_a)

        plane_vector_a = self._normalize(plane_vector_a)
        plane_vector_b = self._normalize(plane_vector_b)

        point = {'x': center['x'] + radius * (math.cos(angle) * plane_vector_a['x'] + math.sin(angle) * plane_vector_b['x']),
                 'y': center['y'] + radius * (math.cos(angle) * plane_vector_a['y'] + math.sin(angle) * plane_vector_b['y']),
                 'z': center['z'] + radius * (math.cos(angle) * plane_vector_a['z'] + math.sin(angle) * plane_vector_b['z'])}
        return point

    def set_center(self, x, y, z):
        self.center = {'x': x, 'y': y, 'z': z}

    def set_axis(self, x, y, z):
        self.axis = {'x': x, 'y': y, 'z': z}
        self.axis = self._normalize(self.axis)

    def axis_random(self):
        self.set_axis(random.random(), random.random(), random.random())

    def set_angular_speed(self, speed):
        self.w_speed = 2 * math.pi * speed

    def set_radius(self, r):
        self.currentRadious = r

    def set_initial_angle(self, angle):
        self.initialAngle = angle
        self.currentAngle = angle

    def angle_random(self):
        random_angle = random.random() * 2 * math.pi
        self.set_initial_angle(random_angle)

    def get_current_degrees(self):
        degrees = (self.currentAngle % (2 * math.pi)) * 180.0 / math.pi
        if degrees < 0:
            degrees += 360
        return degrees

    def get_actual_radius(self):
        current_center = self.center
        if self.lastCloserAttractorIdx != -1:
            current_center = self.attractors[self.lastCloserAttractorIdx]
        distance = math.sqrt((current_center['x'] - self.movingPoint['x'])**2 + (current_center['y'] - self.movingPoint['y'])**2 + (current_center['z'] - self.movingPoint['z'])**2)
        return distance

    def update_angular_speed_by_other_angle_degrees(self, other_angle):
        degrees = self.get_current_degrees()
        diff = degrees - other_angle
        factor = diff / 360.0
        self.w_speed += factor

    def get_current_speed(self):
        return self.w_speed / (2 * math.pi)
    
    def set_influencer_position(self, id, x, y, z):
        #If id is in attractors, set it in attractors
        for attractor in self.attractors:
            if attractor['id'] == id:
                self.set_attractor_position(id, attractor['radius'], x, y, z)
                return
            
        #If id is in repellers, set it in repellers
        for repeller in self.repellers:
            if repeller['id'] == id:
                self.set_repeller_position(id, repeller['radius'], x, y, z)
                return

    def influencer_position(self, id, radius, x, y, z, influencers):
        idx = self.influencer_find(id, influencers)
        if idx == -1:
            idx = self.influencer_available_idx(influencers)
            if idx == -1:
                print("Influencers array is full")
                return
            influencers[idx]['id'] = id
        influencers[idx].update({'radius': radius, 'x': x, 'y': y, 'z': z})

    def influencer_remove(self, id, influencers):
        idx = self.influencer_find(id, influencers)
        if idx != -1:
            influencers[idx]['id'] = -1

    def influencer_find(self, id, influencers):
        for i, influencer in enumerate(influencers):
            if influencer['id'] == id:
                return i
        return -1

    def influencer_available_idx(self, influencers):
        for i, influencer in enumerate(influencers):
            if influencer['id'] == -1:
                return i
        return -1

    def set_attractor_position(self, id, radius, x, y, z):
        self.influencer_position(id, radius, x, y, z, self.attractors)

    def remove_attractor(self, id):
        self.influencer_remove(id, self.attractors)

    def closer_attractor_in_radius(self, radius):
        min_distance = float('inf')
        min_idx = -1
        for i, attractor in enumerate(self.attractors):
            if attractor['id'] == -1:
                continue
            distance = math.sqrt((attractor['x'] - self.movingPoint['x'])**2 + (attractor['y'] - self.movingPoint['y'])**2 + (attractor['z'] - self.movingPoint['z'])**2)
            if distance < min_distance and distance < radius:
                min_distance = distance
                min_idx = i
        return min_idx

    def center_on_closer_attractor_in_radius(self, radius):
        idx = self.closer_attractor_in_radius(radius)
        if idx != -1:
            self.lastCloserAttractorIdx = idx
        if self.lastCloserAttractorIdx != -1:
            closer_attractor = self.attractors[self.lastCloserAttractorIdx]
            self.center = {'x': closer_attractor['x'], 'y': closer_attractor['y'], 'z': closer_attractor['z']}
            self.currentRadious = closer_attractor['radius']

    def set_repeller_position(self, id, radius, x, y, z):
        self.influencer_position(id, radius, x, y, z, self.repellers)

    def remove_repeller(self, id):
        self.influencer_remove(id, self.repellers)

    def repellers_apply(self):
        for repeller in self.repellers:
            if repeller['id'] == -1:
                continue
            distance = math.sqrt((repeller['x'] - self.movingPoint['x'])**2 + (repeller['y'] - self.movingPoint['y'])**2 + (repeller['z'] - self.movingPoint['z'])**2)
            if distance < repeller['radius']:
                repeller_vector = {'x': self.movingPoint['x'] - repeller['x'], 'y': self.movingPoint['y'] - repeller['y'], 'z': self.movingPoint['z'] - repeller['z']}
                repeller_vector = self._normalize(repeller_vector)
                repeller_distance = repeller['radius'] - distance
                self.movingPoint['x'] += repeller_vector['x'] * repeller_distance
                self.movingPoint['y'] += repeller_vector['y'] * repeller_distance
                self.movingPoint['z'] += repeller_vector['z'] * repeller_distance

    def get_position(self):
        return self.movingPoint
    
    def get_color(self):
        return self.colorHex

    def update(self, deltaTimeMs):
        #Update position
        self.deltaTime = deltaTimeMs / 1000.0
        self.currentAngle += self.deltaTime * self.w_speed
        self.center_on_closer_attractor_in_radius(10000000000)
        self.movingPoint = self._rotate(self.currentRadious, self.center, self.axis, self.currentAngle)
        self.repellers_apply()

        #Update color
        degrees = self.get_current_degrees()
        color = colorsys.hsv_to_rgb(degrees / 360.0, 1, 1)
        self.colorHex = '%02x%02x%02x' % (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))

        #Update local communication
        self.update_local_communication(deltaTimeMs)     

        #update musical agent
        self.MusicalAgent.update(deltaTimeMs)

        #update playback timer
        self.playbackTimerMs += deltaTimeMs
        if self.playbackTimerMs >= self.playbackPeriodMs:
            self.playbackTimer_expired = True
            self.playbackTimerMs = 0
        else:
            self.playbackTimer_expired = False



    def update_local_communication(self, deltaTimeMs):
        self.localCommTimerMs += deltaTimeMs
        self.send_local_msg = False
        self.local_message = None
        if self.localCommTimerMs >= self.localCommPeriodMs:
            self.localCommTimerMs = 0
            #Send message through local communication
            self.send_local_msg = True
            #We are sending the current angle degrees
            self.local_message = self.get_current_degrees()
    
    def get_local_message(self):
        return self.send_local_msg, self.local_message
    
    def receive_local_message(self, otherId, message):
        #In this particular case, we are going to update the angular speed of the agent
        #We assume that the message is the angle degrees of the other agent, convert to int in case
        self.update_angular_speed_by_other_angle_degrees(float(message))

    def get_last_closer_attractor(self):
        if self.lastCloserAttractorIdx != -1:
            return self.attractors[self.lastCloserAttractorIdx]['id']
        return -1
    
        