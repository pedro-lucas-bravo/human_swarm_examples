import Utils
import Agent
#https://pypi.org/project/python-osc/ 
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

import random
import threading
import time

lock = threading.Lock()



########## START: OSC Receivers ##########

def connection_answer_handler(address, *args):
    print(f"\nConnected: {args}\n")

def time_answer_handler(address, *args):
    global PONG_RESPONSE
    PONG_RESPONSE = True

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
dispatcher.map("/time", time_answer_handler)

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

def Instantiate_agents_msg(num_agents, limit_radius, shape):
    global AGENTS
    global CURRENT_AGENT_ID_COUNT
    global USE_AUDIO

    # Create message for agents instantiation and positioning
    bundle_agents = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    osc_msg_inst = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
    osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
    if USE_AUDIO:
        bundle_audio = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    osc_msg_inst.add_arg(shape)  # 0: shape=0 for sphere 1 for cube
    osc_msg_inst.add_arg(0)  # 0: movMode=teleport
    for i in range(num_agents):
        CURRENT_AGENT_ID_COUNT = CURRENT_AGENT_ID_COUNT + 1
        # Generate a random position within the limit radius
        init_position = Utils.random_position_within_radius(limit_radius)
        agent = Agent.Agent(id = CURRENT_AGENT_ID_COUNT, init_position= init_position, speed=random.uniform(1000, 3000), limit_radius=limit_radius, type=shape)  # speed is arbitrary, can be adjusted
        AGENTS[CURRENT_AGENT_ID_COUNT] = agent
        # accumulate ids in the message
        osc_msg_inst.add_arg(CURRENT_AGENT_ID_COUNT)

        # Add the agent's initial position to the position message
        osc_msg_pos.add_arg(CURRENT_AGENT_ID_COUNT)
        osc_msg_pos.add_arg(init_position[0])
        osc_msg_pos.add_arg(init_position[1])
        osc_msg_pos.add_arg(init_position[2])

        if USE_AUDIO:
            #Collect the audio bundle for the agent
            oscType = 0 if shape == 0 else 2  # 0: Sine wave for autonomous agents, 1: Saw wave for user controlled agents
            bundle_audio.add_content(agent.MusicalAgent.InstantiationBundle(oscType=oscType).build())  # 0: Sine wave        
            #Play inmediately the agent's sound
            bundle_audio.add_content(agent.MusicalAgent.PlayMsg().build())
            #Assign a random frequency to the agent's sound
            agent.MusicalAgent.BaseFrequency = random.uniform(100, 1000)  # Random frequency between 100 and 1000 Hz

    # Add to agents' instantiation bundle
    bundle_agents.add_content(osc_msg_inst.build())
    bundle_agents.add_content(osc_msg_pos.build())
    if USE_AUDIO:
        bundle_agents.add_content(bundle_audio.build())
    return bundle_agents

def Instantiate_Objects(client, num_agents_autonomous, num_agents_user_controlled):
    #Create instantiation bundle
    instantiation_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    #Message for boundary instantiation
    instantiation_bundle.add_content(Instantiate_Boundary_msg().build())

    #Message for agents instantiation
    instantiation_bundle.add_content(Instantiate_agents_msg(num_agents_autonomous, BOUNDARY['radius'], shape=0).build())  # 0: shape=0 for sphere
    instantiation_bundle.add_content(Instantiate_agents_msg(num_agents_user_controlled, BOUNDARY['radius'], shape=1).build())  # 1: shape=1 for cube

    # Ping the time to continue when there is an answer
    msg_ping = osc_message_builder.OscMessageBuilder(address="/time")
    instantiation_bundle.add_content(msg_ping.build())

    #Send the instantiation bundle
    client.send(instantiation_bundle.build())

############# END: 2 INSTANTIATION #############



############# START: 3 BEHAVIOUR #############

# Config params
DELTA_TIME = 20 # in ms

#Gobal state variables
RUNNING = False
DEFAULT_AUTONOMOUS_AGENTS = 5  # Default number of autonomous agents
DEFAULT_USER_CONTROLLED_AGENTS = 0  # Default number of user controlled agents
USE_AUDIO = True  # Flag to use audio
MAX_ITERATIONS = -1  # Maximum number of iterations for the behaviour loop, if negative, it will run indefinitely
COLLECT_DATA_AND_SAVE = False  # Flag to collect data and save it
PONG_RESPONSE = False  # Flag to check if the pong response has been received

# Update the agents behaviour
def Global_Behaviour(client):
    global AGENTS
    global DELTA_TIME
    global RUNNING
    global DEFAULT_AUTONOMOUS_AGENTS
    global DEFAULT_USER_CONTROLLED_AGENTS
    global COLLECT_DATA_AND_SAVE
    global USE_AUDIO
    global PONG_RESPONSE

    # Initialization
    Instantiate_Objects(client, DEFAULT_AUTONOMOUS_AGENTS, DEFAULT_USER_CONTROLLED_AGENTS)

    while not PONG_RESPONSE:
        time.sleep(DELTA_TIME / 1000.0)
    
    PONG_RESPONSE = False  # Reset flag

    time.sleep(1)  # Wait fopr 1 sec

    if COLLECT_DATA_AND_SAVE:
        delta_time_data = []
        msg_metrics_recorder_start = osc_message_builder.OscMessageBuilder(address="/metrics/recorder/start")
        bundle_metrics = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle_metrics.add_content(msg_metrics_recorder_start.build())
        client.send(bundle_metrics.build())
    if MAX_ITERATIONS > 0:
        iterations = 0

    # Update the agents behaviour
    while RUNNING:
        start_time = time.time()  # Start time for the loop
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
        if USE_AUDIO:
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

                if USE_AUDIO:
                    #Update the agent's musical agent
                    osc_audio = agent.MusicalAgent.update(agent.limit_radius, agent.position)
                    audio_bundle.add_content(osc_audio.build())
                    
        bundle.add_content(osc_msg_pos.build())
        if USE_AUDIO:
            bundle.add_content(audio_bundle.build())
        #Send all agents info to Unity app
        client.send(bundle.build())

        #sleep delta time of this thread
        time.sleep(DELTA_TIME / 1000.0)

        elapsed_time = time.time() - start_time # Elapsed time in milliseconds
        if COLLECT_DATA_AND_SAVE:
            delta_time_data.append(elapsed_time)
        if MAX_ITERATIONS > 0:
            iterations += 1
            if iterations >= MAX_ITERATIONS:
                RUNNING = False

    # Save the data if needed
    if COLLECT_DATA_AND_SAVE:
        msg_metrics_recorder_stop = osc_message_builder.OscMessageBuilder(address="/metrics/recorder/stop")
        msg_metrics_save = osc_message_builder.OscMessageBuilder(address="/metrics/recorder/save")
        bundle_metrics = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        bundle_metrics.add_content(msg_metrics_recorder_stop.build())
        bundle_metrics.add_content(msg_metrics_save.build())      
        client.send(bundle_metrics.build())
        filename_dated = f"data/delta_time_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        Utils.save_to_file(filename_dated, delta_time_data)

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
    global MAX_ITERATIONS
    global COLLECT_DATA_AND_SAVE
    global USE_AUDIO

    USE_AUDIO = True #Change here to decide if experiment will use audio or not

    MAX_ITERATIONS = 500
    COLLECT_DATA_AND_SAVE = True  # Set to True to collect and save data
    if USE_AUDIO:
        number_of_autonomous_agents = [1, 2, 4, 8, 16, 32, 64, 128, 249]  #[23, 24, 25, 26]
    else:
        number_of_autonomous_agents = [2 ** i for i in range(0, 12)]#[80, 249, 250]#  # [2, 4, 8, ..., 2048]
        #number_of_autonomous_agents = []
        number_of_autonomous_agents.append(2608)
    
    client.send_message("/connect", [local_ip, local_port])    
    time.sleep(1)  # Wait for the connection to be established
    client.send_message("/metrics/activate", [])    
    for num_agents in number_of_autonomous_agents:
        print(f"Running experiment with {num_agents} autonomous agents")
        DEFAULT_AUTONOMOUS_AGENTS = num_agents
        RUNNING = True
        behaviour_thread = threading.Thread(target=lambda: Global_Behaviour(client))             
        behaviour_thread.start()
        behaviour_thread.join()  # Wait for the behaviour thread to finish
        time.sleep(1)  # Wait before cleaning up
        Remove_All(client)
        print(f"Experiment with {num_agents} autonomous agents completed")
        time.sleep(2)  # Wait before starting the next experiment
    print("All experiments completed.")
    client.send_message("/metrics/deactivate", [])

############# END: EXPERIMENT SETTING #############

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
        elif command == "experiment":
            run_experiment()
        elif command == "stop":
            # Stop the agents behaviour
            RUNNING = False
        #if command contains "v" as the first word and then a number, it will set the speed of all agents
        elif command[0] == "v" and Utils.is_float(command[1:].strip()):
            try:
                speed_factor = float(command[1:])
                with lock:
                    for agentId in AGENTS:
                        agent = AGENTS[agentId]
                        agent.set_speed_factor(speed_factor)
                print("All agents speed factor set to:", speed_factor)
            except:
                print("Invalid command")
        #Activate metrics
        elif command == "ma":
            # Send the message to activate metrics
            client.send_message("/metrics/activate", [])
        #Deactivate metrics
        elif command == "md":
            # Send the message to deactivate metrics
            client.send_message("/metrics/deactivate", [])
        #Record metrics
        elif command == "mr":
            # Send the message to record metrics
            client.send_message("/metrics/recorder/start", [])
        #Stop recording metrics
        elif command == "ms":
            # Send the message to stop recording metrics
            client.send_message("/metrics/recorder/stop", [])
        #Save recorded metrics
        elif command == "msv":
            # Send the message to save recorded metrics
            client.send_message("/metrics/recorder/save", [])
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

