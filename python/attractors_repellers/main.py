import AgentBehaviour 
import MusicalAgent
#https://pypi.org/project/python-osc/ 
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

import threading
import time

lock = threading.Lock()

########## START: OSC Receivers ##########

def connection_answer_handler(address, *args):
    print(f"\nConnected: {args}\n")

def influencer_position_handler(address, *args):
    global AGENTS
    (id, x, y, z) = args
    with lock:
        for agentId in AGENTS:
            agent = AGENTS[agentId]
            agent.set_influencer_position(id, x, y, z)

def local_communication_handler(address, *args):
    global AGENTS
    if len(args) % 3 == 0:
        for i in range(0, len(args), 3):
            receiverId = args[i]
            senderId = args[i+1]
            message = args[i+2]
            with lock:
                if receiverId in AGENTS:
                    AGENTS[receiverId].receive_local_message(senderId, message)

########## END: OSC Receivers ##########

############# START: 1 NETWORK #############

# Unity app network configuration
external_ip = "127.0.0.1"
external_port = 6011

# This PC network configuration
local_ip = "127.0.0.1"
local_port = 6010

# Create the client
client = udp_client.SimpleUDPClient(external_ip, external_port)

# Create the listener
dispatcher = Dispatcher()

# Deine OSC mapping receivers
dispatcher.map("/test/alive/", connection_answer_handler)
dispatcher.map("/agents/position/id", influencer_position_handler)
dispatcher.map("/agents/localcomm/recv", local_communication_handler)


# Create the server in a parallel thread
server = osc_server.ThreadingOSCUDPServer((local_ip, local_port), dispatcher)
print("Serving on {}".format(server.server_address))
server_thread = threading.Thread(target=lambda: server.serve_forever())
server_thread.start()

############# END: 1 NETWORK #############

############# START: 2 INSTANTIATION #############

AGENTS = {}

# Build the message to instantiate agents and send it to the Unity app
def Instantiate_Agents(client):
    #number of agents
    num_agents = 10

    # Local communication settings
    localcomm_radius = 3000 # in mm
    localcomm_latency = 500 # in ms
    localcomm_show_feedback = True

    #Create instantiation bundle
    instantiation_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    # Create message for agents instantiation
    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
    osc_msg.add_arg(0) # 0: shape=sphere
    osc_msg.add_arg(0) # 0: movMode=teleport
    for i in range(num_agents):
        id = i + 1
        #accumulate ids in the message
        osc_msg.add_arg(id)

    instantiation_bundle.add_content(osc_msg.build())

    #Create the message for  local communication settings
    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/localcomm")
    osc_msg.add_arg(localcomm_radius)
    osc_msg.add_arg(localcomm_latency)
    osc_msg.add_arg(1 if localcomm_show_feedback else 0)
    instantiation_bundle.add_content(osc_msg.build())

    #Create bundle for musical agent in unity
    audio_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)   

    # Agents behaviour instantiation
    global AGENTS
    for i in range(num_agents):
        id = i + 1
        agent = AgentBehaviour.AgentBehaviour(id) # internally it assigns a random axis and angle
        AGENTS[id] = agent
        # Add Musical Agent instantiation OSC messages: oscType, attack, decay, sustain, release
        audio_bundle.add_content(agent.MusicalAgent.InstantiationBundle(2, 0.01, 0.1, 0.3, 0.2))

    #Send the instantiation bundle
    instantiation_bundle.add_content(audio_bundle.build())
    client.send(instantiation_bundle.build())

#Instantiate an influencer: attractor or repeller
def Instantiate_Influencer(id, radius, x, y, z, color_hex, client):
    instantiation_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
    osc_msg.add_arg(1) # 1: shape=cube
    osc_msg.add_arg(0) # 0: movMode=teleport
    osc_msg.add_arg(id)
    instantiation_bundle.add_content(osc_msg.build())

    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/color/id")
    osc_msg.add_arg(id)
    osc_msg.add_arg(color_hex)
    instantiation_bundle.add_content(osc_msg.build())

    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/radius/id")
    osc_msg.add_arg(id)
    osc_msg.add_arg(radius)
    osc_msg.add_arg(0.2) #alpha
    osc_msg.add_arg(color_hex)
    instantiation_bundle.add_content(osc_msg.build())

    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
    osc_msg.add_arg(id)
    osc_msg.add_arg(x)
    osc_msg.add_arg(y)
    osc_msg.add_arg(z)
    instantiation_bundle.add_content(osc_msg.build())

    client.send(instantiation_bundle.build())

    return {'id': id, 'radius': radius, 'x': x, 'y': y, 'z': z}


#Instantiate all influencers
def Instantiate_all_influencers(client):
    
    #attractors
    attractors = []
    influencer = Instantiate_Influencer(1000, 5000, 0, 0, 0, "00e5ff", client)
    attractors.append(influencer)
    influencer = Instantiate_Influencer(1001, 6000, 7000, 0, 0, "00ffd5", client)
    attractors.append(influencer)

    #repellers
    repellers = []
    influencer = Instantiate_Influencer(2000, 10000, 0, 20000, 0, "ff0000", client)
    repellers.append(influencer)
    influencer = Instantiate_Influencer(2001, 8000, 0, -15000, 0, "ff0000", client)
    repellers.append(influencer)

    return attractors, repellers

############# END: 2 INSTANTIATION #############

############# START: 3 BEHAVIOUR #############

# Config params
DELTA_TIME = 30 # in ms

#Gobal state variables
RUNNING = False

# Update the agents behaviour
def Global_Behaviour(client):
    global AGENTS
    global DELTA_TIME
    global ALL_ANGULAR_SPEED_FACTOR
    global RUNNING
    global EXTERNAL_INFLUENCERS

    # Initialization
    Instantiate_Agents(client)
    attractors, repellers = Instantiate_all_influencers(client)


    # Initialize agents
    for agentId in AGENTS:
        agent = AGENTS[agentId]
        agent.set_angular_speed(0.0)
        for attractor in attractors:
            agent.set_attractor_position(attractor['id'], attractor['radius'], attractor['x'], attractor['y'], attractor['z'])
        for repeller in repellers:
            agent.set_repeller_position(repeller['id'], repeller['radius'], repeller['x'], repeller['y'], repeller['z'])
        

    # Update the agents behaviour
    while RUNNING:
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        with lock:
            for agentId in AGENTS:                
                agent = AGENTS[agentId]

                #Update agent
                agent.update(DELTA_TIME)

                #Prepare OSC Agent Position
                position = agent.get_position()
                osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
                osc_msg.add_arg(agent.id)
                osc_msg.add_arg(position['x'])
                osc_msg.add_arg(position['y'])
                osc_msg.add_arg(position['z'])
                bundle.add_content(osc_msg.build())

                #Prepare OSC Agent Color
                color = agent.get_color()
                osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/color/id")
                osc_msg.add_arg(agent.id)
                osc_msg.add_arg(color)
                bundle.add_content(osc_msg.build())

                #Prepare OSC Agent Local Communication
                send, message = agent.get_local_message()
                if send:
                    osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/localcomm/send")
                    osc_msg.add_arg(agent.id)
                    osc_msg.add_arg(message)
                    bundle.add_content(osc_msg.build())                  

                #Playback note
                if agent.playbackTimer_expired:
                    bundle.add_content(agent.MusicalAgent.OSC_MSG_MidiNote(70, 127, agent.MusicalAgent.CalculateNoteLengthFromAngularSpeed(agent.get_current_speed()))) #Play note 70 with velocity 127 for some ms

                #Turn off sound when musical agent finish
                if agent.MusicalAgent.SendNoteOff:
                    bundle.add_content(agent.MusicalAgent.OSC_MSG_MidiNote(70, 0, 0)) #Turn off note 70 (velocity 0)

                #############  Audio Mapping Messages ############# 
                bundle.add_content(agent.MusicalAgent.OSC_MSG_MAP_Sound_MovementDynamics(agent.get_current_degrees(), agent.get_current_speed(), agent.get_actual_radius(), agent.get_last_closer_attractor()))
                    
        
        #Send all agents info to Unity app
        client.send(bundle.build())

        #sleep delta time of this thread
        time.sleep(DELTA_TIME / 1000.0)


############# END: 3 BEHAVIOUR #############

############# START: 4 MUSICAL AGENT #############

# TODO: Implement the musical agent

############# END: 4 MUSICAL AGENT #############

############# START: 5 DESTROY #############

def Remove_All(client):
    global AGENTS
    #Send remove messages
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    with lock:
        for agentId in AGENTS:
            osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
            osc_msg.add_arg(agentId)
            bundle.add_content(osc_msg.build())

            for attractor in AGENTS[agentId].attractors:
                osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
                osc_msg.add_arg(attractor['id'])
                bundle.add_content(osc_msg.build())
            for repeller in AGENTS[agentId].repellers:
                osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
                osc_msg.add_arg(repeller['id'])
                bundle.add_content(osc_msg.build())
        client.send(bundle.build())
        # Clean the agents
        AGENTS = {}

############# END: 5 DESTROY #############

############## USER CONTROL ##############

# Create a loop to catch input from keyboard
while True:
    try:
        # Get the input from the keyboard
        command = input("Enter a command: ")
        if command == "connect":
            # Send the local IP and port to the Unity app for connection
            client.send_message("/connect", [local_ip, local_port])
            
        elif command == "run":
            # Send the local IP and port to the Unity app for connection
            client.send_message("/connect", [local_ip, local_port])
            # Run in a parallel thread the agents behaviour
            RUNNING = True
            behaviour_thread = threading.Thread(target=lambda: Global_Behaviour(client))             
            behaviour_thread.start() 
        elif command == "stop":
            # Stop the agents behaviour
            RUNNING = False
        #if command contains "a" as teh first word and then a number, it will set the angular speed of all agents
        #WARNING: Be careful if including other commands that start with "a"
        elif command[0] == "a":
            try:
                angular_speed_factor = float(command[1:])
                with lock:
                    for agentId in AGENTS:
                        agent = AGENTS[agentId]
                        agent.set_angular_speed(angular_speed_factor)
                print("All agents angular speed factor set to:", angular_speed_factor)
            except:
                print("Invalid command")
        elif command == "clean":
            RUNNING = False
            Remove_All(client)
            print("All agents cleaned")
        elif command == "exit":
            Remove_All(client)
            # Stop the server
            server.shutdown()
            RUNNING = False
            break
        elif command == "test":
            client.send_message("/agents/instantiate/id", [0, 0, 1])
            musicalAgent = MusicalAgent.MusicalAgent(1, client)
            musicalAgent.InstatiateExternal()
            musicalAgent.SetOscillator(2)
            musicalAgent.ADSR(0.1, 0.1, 0.3, 0.2)
        elif command == "noteon":            
            musicalAgent.MidiNote(80, 100)
        elif command == "noteoff":
            musicalAgent.MidiNote(80, 0)
        elif command == "freq1":
            musicalAgent.SetFrequency(220)
        elif command == "freq2":
            musicalAgent.SetFrequency(440)
        else:
            print("Command does not exist")

            
    except KeyboardInterrupt:
        Remove_All(client)
        # Stop the server
        server.shutdown()
        RUNNING = False
        break
    time.sleep(0.1)

############## END USER CONTROL ##############

