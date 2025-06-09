import Utils
import Agent
#https://pypi.org/project/python-osc/ 
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

import numpy as np

import random
import threading
import time

lock = threading.Lock()



########## START: OSC Receivers ##########

def connection_answer_handler(address, *args):
    print(f"\nConnected: {args}\n")

def interative_agents_position_handler(address, *args):
    global AGENTS
    (id, x, y, z) = args # We are assuming that one only agent is sent at a time
    with lock:
        AGENTS[id].position = np.array([x, y, z])  # Update the agent's position
    print(f"Agent {id} position updated to: ({x}, {y}, {z})")

########## END: OSC Receivers ##########



########## START: Helpers ##########

def agent_radius_msg(osc_msg_radius, agent, color):
    osc_msg_radius.add_arg(agent.id)  # Add the agent's ID to the message
    osc_msg_radius.add_arg(agent.local_radius)
    osc_msg_radius.add_arg(0.1)  # 0.1: alpha for the radius color    
    osc_msg_radius.add_arg(color) 

########## END: Helpers ##########



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
dispatcher.map("/agents/position/id", interative_agents_position_handler)

# Create the server in a parallel thread
server = osc_server.ThreadingOSCUDPServer((local_ip, local_port), dispatcher)
print("Serving on {}".format(server.server_address))
server_thread = threading.Thread(target=lambda: server.serve_forever())
server_thread.start()

############# END: 1 NETWORK #############



############# START: 2 INSTANTIATION #############

BOUNDARY = {'position': {'x': 0, 'y': 0, 'z': 0}, 'radius': 10000, 'alpha': 0.1, 'color': '00ff00'} # Boundary of the world
AGENTS = {}
CURRENT_AGENT_ID_COUNT = 0


def Instantiate_Boundary_msg():
    global BOUNDARY
    # Message for boundary instantiation
    osc_msg = osc_message_builder.OscMessageBuilder(address="/boundary/add/id")
    osc_msg.add_arg(0)  # ID = 0
    osc_msg.add_arg(0)  # 0: type=sphere
    osc_msg.add_arg(BOUNDARY['position']['x'])
    osc_msg.add_arg(BOUNDARY['position']['y'])
    osc_msg.add_arg(BOUNDARY['position']['z'])
    osc_msg.add_arg(BOUNDARY['radius'])
    osc_msg.add_arg(BOUNDARY['alpha'])  # color transparency
    osc_msg.add_arg(BOUNDARY['color'])  # color in hex format   
    
    return osc_msg

def Instantiate_agents_msg(num_agents, local_radius, limit_radius, shape):
    global AGENTS
    global CURRENT_AGENT_ID_COUNT
    # Create message for agents instantiation and positioning
    bundle_agents = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    osc_msg_inst = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
    osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
    osc_msg_radius = osc_message_builder.OscMessageBuilder(address="/agents/radius/id")
    bundle_audio = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    osc_msg_inst.add_arg(shape)  # 0: shape=0 for sphere 1 for cube
    osc_msg_inst.add_arg(0)  # 0: movMode=teleport
    for i in range(num_agents):
        CURRENT_AGENT_ID_COUNT = CURRENT_AGENT_ID_COUNT + 1
        # Generate a random position within the limit radius
        init_position = Utils.random_position_within_radius(limit_radius)
        agent = Agent.Agent(allAgents=AGENTS, id = CURRENT_AGENT_ID_COUNT, init_position= init_position, speed=random.uniform(1000, 3000), local_radius=local_radius, limit_radius=limit_radius, type=shape)  # speed is arbitrary, can be adjusted
        AGENTS[CURRENT_AGENT_ID_COUNT] = agent
        # accumulate ids in the message
        osc_msg_inst.add_arg(CURRENT_AGENT_ID_COUNT)

        # Add the agent's initial position to the position message
        osc_msg_pos.add_arg(CURRENT_AGENT_ID_COUNT)
        osc_msg_pos.add_arg(init_position[0])
        osc_msg_pos.add_arg(init_position[1])
        osc_msg_pos.add_arg(init_position[2])

        #Add the agent's radius to the radius message
        agent_radius_msg(osc_msg_radius, agent, agent.radius_normal_color)

        #Collect the audio bundle for the agent
        oscType = 0 if shape == 0 else 1  # 0: Sine wave for autonomous agents, 1: Saw wave for user controlled agents
        bundle_audio.add_content(agent.MusicalAgent.InstantiationBundle(oscType=oscType).build())  # 0: Sine wave        

    # Add to agents' instantiation bundle
    bundle_agents.add_content(osc_msg_inst.build())
    bundle_agents.add_content(osc_msg_pos.build())
    bundle_agents.add_content(osc_msg_radius.build())  #ADDED: Add the radius message to the bundle
    bundle_agents.add_content(bundle_audio.build())
    return bundle_agents

def Instantiate_Objects(client, num_agents_autonomous, num_agents_user_controlled, local_radius):
    #Create instantiation bundle
    instantiation_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    #Message for boundary instantiation
    instantiation_bundle.add_content(Instantiate_Boundary_msg().build())

    #Message for agents instantiation
    instantiation_bundle.add_content(Instantiate_agents_msg(num_agents_autonomous, local_radius, BOUNDARY['radius'], shape=0).build())  # 0: shape=0 for sphere
    instantiation_bundle.add_content(Instantiate_agents_msg(num_agents_user_controlled, local_radius, BOUNDARY['radius'], shape=1).build())  # 1: shape=1 for cube

    #Send the instantiation bundle
    client.send(instantiation_bundle.build())

############# END: 2 INSTANTIATION #############



############# START: 3 BEHAVIOUR #############

# Config params
DELTA_TIME = 30 # in ms
LOCAL_RADIUS = 3000  # Local radius for agents, can be adjusted
DEFAULT_AUTONOMOUS_AGENTS = 5  # Default number of autonomous agents
DEFAULT_USER_CONTROLLED_AGENTS = 2  # Default number of user controlled agents

#Gobal state variables
RUNNING = False

# Update the agents behaviour
def Global_Behaviour(client):
    global AGENTS
    global DELTA_TIME
    global RUNNING
    global LOCAL_RADIUS 
    global DEFAULT_AUTONOMOUS_AGENTS
    global DEFAULT_USER_CONTROLLED_AGENTS

    # Initialization
    Instantiate_Objects(client, DEFAULT_AUTONOMOUS_AGENTS, DEFAULT_USER_CONTROLLED_AGENTS, LOCAL_RADIUS)  # Instantiate 5 agents

    # Update the agents behaviour
    while RUNNING:
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
        osc_msg_radius = osc_message_builder.OscMessageBuilder(address="/agents/radius/id")
        audio_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        with lock:
            for agentId in AGENTS:                
                agent = AGENTS[agentId]

                #Update agent
                agent.update(DELTA_TIME)

                #Prepare OSC Agent Position if type is 0 (autonomous)
                if agent.type == 0:  # Assuming type 0 is autonomous
                    position = agent.position                    
                    osc_msg_pos.add_arg(agent.id)
                    osc_msg_pos.add_arg(position[0])
                    osc_msg_pos.add_arg(position[1])
                    osc_msg_pos.add_arg(position[2])                    

                nearby_agents = agent.get_nearby_agents()
                #Update the agent's musical agent
                osc_audio = agent.MusicalAgent.update(agent.limit_radius, agent.position, agent.velocity, nearby_agents)
                if osc_audio is not None:                    
                    audio_bundle.add_content(osc_audio.build())

                #Update the agent's radius color feedback when there are nearby agents
                if len(nearby_agents) > 0:
                    agent_radius_msg(osc_msg_radius, agent, agent.radius_detection_color)
                else:
                    agent_radius_msg(osc_msg_radius, agent, agent.radius_normal_color)
                    
        bundle.add_content(osc_msg_pos.build())
        bundle.add_content(audio_bundle.build())
        bundle.add_content(osc_msg_radius.build())

        #Send all agents info to Unity app
        client.send(bundle.build())

        #sleep delta time of this thread
        time.sleep(DELTA_TIME / 1000.0)

############# END: 3 BEHAVIOUR #############



############# START: 4 DESTROY #############

def Remove_All(client):
    global BOUNDARY   
    global AGENTS
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)    
    with lock:
        # Remove the boundary
        osc_msg = osc_message_builder.OscMessageBuilder(address="/boundary/remove/id")
        osc_msg.add_arg(0)  # ID = 0
        bundle.add_content(osc_msg.build())
        # Remove all agents
        osc_msg = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
        for agentId in AGENTS:            
            osc_msg.add_arg(agentId)
            bundle.add_content(osc_msg.build())
        client.send(bundle.build())
        # Clean the agents
        AGENTS = {}

############# END: 4 DESTROY #############

############# START: EXPERIMENT SETTING #############

def run_experiment():
    global RUNNING
    global DEFAULT_AUTONOMOUS_AGENTS

    duration_per_experiment = 60  # seconds
    number_of_autonomous_agents = [2, 4, 8, 16, 32]
    
    client.send_message("/connect", [local_ip, local_port])    
    
    for num_agents in number_of_autonomous_agents:
        print(f"Running experiment with {num_agents} autonomous agents")
        client.send_message("/recorder/start", []) # Start recording in Unity app
        DEFAULT_AUTONOMOUS_AGENTS = num_agents
        RUNNING = True
        behaviour_thread = threading.Thread(target=lambda: Global_Behaviour(client))             
        behaviour_thread.start()
        time.sleep(duration_per_experiment)  # Run the experiment for the specified duration
        RUNNING = False
        behaviour_thread.join()  # Wait for the behaviour thread to finish
        client.send_message("/recorder/stop", [])  # Stop recording in Unity app
        time.sleep(1)  # Wait before cleaning up
        Remove_All(client)
        print(f"Experiment with {num_agents} autonomous agents completed")
        time.sleep(1)  # Wait before starting the next experiment
    print("All experiments completed.")    

############# END: EXPERIMENT SETTING #############

############## USER CONTROL ##############s

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
        #if command contains "v" as the first word and then a number, it will set the speed of all agents
        elif command[0] == "v" and  Utils.is_float(command[1:].strip()):
            try:
                speed_factor = float(command[1:])
                with lock:
                    for agentId in AGENTS:
                        agent = AGENTS[agentId]
                        agent.set_speed_factor(speed_factor)
                print("All agents speed factor set to:", speed_factor)
            except:
                print("Invalid command")
        #Set the radius of all agents
        elif command[0] == "r" and Utils.is_float(command[1:].strip()):
            try:
                radius = float(command[1:])
                with lock:
                    osc_msg_radius = osc_message_builder.OscMessageBuilder(address="/agents/radius/id")
                    for agentId in AGENTS:
                        agent = AGENTS[agentId]
                        LOCAL_RADIUS = radius  # Update the global local radius
                        agent.local_radius = radius
                print("All agents radius set to:", radius)
            except:
                print("Invalid command")
        #Instantiate a number of agents
        elif (command.startswith("ia") or command.startswith("iu")) and command[2:].strip().isdigit():
            try:
                num_agents = int(command[2:])
                with lock:
                    shape = 0 if command.startswith("ia") else 1  # 0: autonomous agents, 1: user controlled agents
                    osc_bundle = Instantiate_agents_msg(num_agents, LOCAL_RADIUS, BOUNDARY['radius'], shape=shape)  # 0: shape=0 for sphere
                client.send(osc_bundle.build())
                print("Instantiated", num_agents, "agents")
            except:
                print("Invalid command")
        #Remove a number of agents
        elif (command.startswith("da") or command.startswith("du")) and command[2:].strip().isdigit():
            try:
                num_agents = int(command[2:])
                with lock:
                    shape = 0 if command.startswith("da") else 1  # 0: autonomous agents, 1: user controlled agents
                    osc_remove = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
                    agentsToRemove = [agentId for agentId in AGENTS if AGENTS[agentId].type == shape]
                    #Reverse the list
                    agentsToRemove.reverse()
                    cremove_count = 0
                    for i in range(num_agents):
                        if len(agentsToRemove) == 0:
                            #print("No agents to remove")
                            break
                        # Randomly select an agent to remove
                        agentId = agentsToRemove[0]
                        osc_remove.add_arg(agentId)
                        del AGENTS[agentId]
                        del agentsToRemove[0]
                        cremove_count += 1
                
                if len(osc_remove.args) != 0:
                    client.send(osc_remove.build())
                    print("Removed", cremove_count, "agents")
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
        elif command == "experiment":
            run_experiment()
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

