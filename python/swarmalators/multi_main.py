import SwarmalatorsGUI as SGUI
import Swarmalator
import MusicalSwarmalator

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder

import threading
import time
import multiprocessing
import math

lock = threading.Lock()

########## START: OSC Receivers ##########

def connection_answer_handler(address, *args):
    print(f"\nConnected: {args}\n")

def interactive_agent_position_handler(address, *args):
    global AGENTS_interactive
    (id, x, y, z) = args
    with lock:
        agent = AGENTS_interactive[id]
        agent.SetFromScalePosition(x * 0.001, y * 0.001, z * 0.001)
        print(f"Interactive agent {id} position: {x}, {y}, {z}")

def interactive_agent_control_handler(address, *args):
    global AGENTS_interactive
    global TOTAL_TIME_MS
    #agent_id control_type=0:left_click,1:right_click control_value=1:press,0:release...
    (id, control_type, control_value) = args
    if control_type == 1 and control_value == 1:
        with lock:        
            if id in AGENTS_interactive:
                agent = AGENTS_interactive[id]
                agent.ResetOscillator(TOTAL_TIME_MS / 1000.0)
                print(f"Interactive agent {id} control: {control_type}, {control_value}")

########## END: OSC Receivers ##########

############# START: NETWORK #############

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
dispatcher.map("/agents/position/id", interactive_agent_position_handler)
dispatcher.map("/agents/control", interactive_agent_control_handler)

############# END: NETWORK #############

##########  Instantiate Agents ##########

AGENTS = []
N = 20
J = 0.1
K = 1.0
SPEED = 1.0
N_interactive = 0
BASE_interactive_ID = 1000
AGENTS_interactive = {}
USE_AUDIO = False

# Build the message to instantiate agents and send it to the Unity app
def Instantiate_Agents(client):
    global N
    global AGENTS
    global J
    global K
    global SPEED
    global AGENTS_interactive
    global USE_AUDIO

    #number of agents
    num_agents = N - len(AGENTS)
    if num_agents == 0:
        return
    
    #Create instantiation bundle
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    if num_agents > 0:#Add agents       

        # Create message for agents instantiation
        osc_msg_inst = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
        osc_msg_inst.add_arg(0) # 0: shape=sphere
        osc_msg_inst.add_arg(0) # 0: movMode=teleport

        #Create audio bundle
        if USE_AUDIO:
            bundle_audio = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        #create message for position
        osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
        last_id = len(AGENTS)
        for i in range(num_agents):
            id = last_id + i + 1
            #accumulate ids in the message
            osc_msg_inst.add_arg(id)
            osc_msg_pos.add_arg(id)
            #Create the swarmal
            agent = Swarmalator.Swarmalator(id, False)
            agent.J = J
            agent.K = K
            agent.Speed = SPEED
            agent.AssignRandomPosition(1.0)
            #Add position to the message
            position = agent.ScaledPosition()
            osc_msg_pos.add_arg(int(position[0] * 1000))
            osc_msg_pos.add_arg(int(position[1] * 1000))
            osc_msg_pos.add_arg(int(position[2] * 1000))

            #Add musical agent to bundle (osc_type , attack, decay, sustain , release , phase, amplitude, velocity)
            if USE_AUDIO:
                bundle_audio.add_content(agent.MusicalAgent.InstantiationBundle_and_Play(3, 0.01, 0, 0.2, 0.2, agent.Phase, agent.oscillator, agent.ScaledVelocity()))

            #Add the agent to the list
            AGENTS.append(agent)       
        
        #Add instantiation message to the bundle
        bundle.add_content(osc_msg_inst.build())
        #Add position message to the bundle
        bundle.add_content(osc_msg_pos.build())   
        #Add audio bundle to the main bundle
        if USE_AUDIO:
            bundle.add_content(bundle_audio.build())
    else:#Remove agents
        num_agents = -num_agents
        # Create message for agents deletion
        osc_msg_rem = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")

        for i in range(num_agents):
            agent = AGENTS.pop()
            #accumulate ids in the message
            osc_msg_rem.add_arg(agent.ID)

        #Add remove message to the bundle
        bundle.add_content(osc_msg_rem.build())

    #Set others to the agents (either, when adding or removing agents)
    for i in range(len(AGENTS)):
        AGENTS[i].SetOthers([agent for agent in AGENTS if agent != AGENTS[i]] + list(AGENTS_interactive.values()))
    
    #Send the instantiation bundle
    client.send(bundle.build())

def Instantiate_Interactive_Agent(client):
    global N_interactive
    global AGENTS_interactive
    global BASE_interactive_ID
    global AGENTS

    #number of agents
    num_agents = N_interactive - len(AGENTS_interactive)
    if num_agents == 0:
        return
    
    #Create instantiation bundle
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    if num_agents > 0:#Add agents       

        # Create message for agents instantiation
        osc_msg_inst = osc_message_builder.OscMessageBuilder(address="/agents/instantiate/id")
        osc_msg_inst.add_arg(1) # 0: shape=cube
        osc_msg_inst.add_arg(0) # 0: movMode=teleport

        #create message for position
        osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")        
        last_id = len(AGENTS_interactive)
        for i in range(num_agents):
            id = BASE_interactive_ID + last_id + i + 1
            #accumulate ids in the message
            osc_msg_inst.add_arg(id)
            osc_msg_pos.add_arg(id)
            #Create the swarmalator
            agent = Swarmalator.Swarmalator(id, True)
            agent.J = J
            agent.K = K
            agent.Speed = SPEED
            agent.AssignRandomPosition(1.0)
            #Add position to the message
            position = agent.ScaledPosition()
            osc_msg_pos.add_arg(int(position[0] * 1000))
            osc_msg_pos.add_arg(int(position[1] * 1000))
            osc_msg_pos.add_arg(int(position[2] * 1000))
            #Add the agent to the list
            AGENTS_interactive[id] = agent

        #Add instantiation message to the bundle
        bundle.add_content(osc_msg_inst.build())
        #Add position message to the bundle
        bundle.add_content(osc_msg_pos.build())
    else:#Remove agents
        num_agents = -num_agents
        # Create message for agents deletion
        osc_msg_rem = osc_message_builder.OscMessageBuilder(address="/agents/remove/id")
        # Delete teh last num_agents agents
        for i in range(num_agents):
            agent = AGENTS_interactive.popitem()
            #accumulate ids in the message
            osc_msg_rem.add_arg(agent[0])   

        #Add remove message to the bundle
        bundle.add_content(osc_msg_rem.build())

     #Set others to the agents (either, when adding or removing agents)
    for i in range(len(AGENTS)):
        AGENTS[i].SetOthers([agent for agent in AGENTS if agent != AGENTS[i]] + list(AGENTS_interactive.values()))
    
    #Send the instantiation bundle
    client.send(bundle.build())



############# END: Instantiate Agents #############

############# START: BEHAVIOUR #############

# Config params
DELTA_TIME_MS = 20 # in ms
TOTAL_TIME_MS = 0

#Gobal state variables
RUNNING = False

#Multi-threaded agent task
def agent_task(worker_id, agents_data):
    results = {}
    for agent_data in agents_data:
        id, myPhase, myPosition, phases, positions, dt, current_time, J, K, speed, amplitude, frequency = agent_data
        result = Swarmalator.Swarmalator.calculate_params(dt, current_time, myPhase, myPosition, phases, positions, J, K, speed, amplitude, frequency)
        results[id] = result
    return results

# Update the agents behaviour
def Global_Behaviour(client):    

    global AGENTS
    global DELTA_TIME_MS
    global TOTAL_TIME_MS
    global RUNNING
    global USE_AUDIO

    TOTAL_TIME_MS = 0

    # Initialization
    Instantiate_Agents(client)      
    Instantiate_Interactive_Agent(client)    

    #multithreading
    #manager = multiprocessing.Manager()
    num_workers = multiprocessing.cpu_count()

    # Create a pool of worker processes
    pool = multiprocessing.Pool(num_workers)

    try:
        # Update the agents behaviour
        while RUNNING:                
            start_time = time.time()

            bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
            osc_msg_pos = osc_message_builder.OscMessageBuilder(address="/agents/position/id")
            osc_msg_color = osc_message_builder.OscMessageBuilder(address="/agents/color/id")   
            if USE_AUDIO:
                audio_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)         

            with lock: 
                start_time_test = time.time()     
                jobs = []
                for i in range(num_workers):
                    subset_len = math.ceil(len(AGENTS) / num_workers)
                    start_index = i * subset_len
                    end_index = min((i + 1) * subset_len, len(AGENTS))
                    agents_subset = AGENTS[start_index:end_index]
                    jobs.append(pool.apply_async(agent_task, args=(i, [[agent.ID, agent.Phase, agent.Position, 
                                                       [other.Phase for other in agent.Others if other.ID != agent.ID],
                                                       [other.Position for other in agent.Others if other.ID != agent.ID],
                                                       DELTA_TIME_MS / 1000.0, TOTAL_TIME_MS / 1000.0, agent.J, agent.K, agent.Speed, agent.Amplitude, agent.Frequency] 
                                                       for agent in agents_subset])
                                                )
                    )
                    if end_index == len(AGENTS):
                        break
                #measure time test
                #print("Time to create jobs:", time.time() - start_time_test)
                 # Retrieve the results as soon as they're ready
                results_dict = {}
                for job in jobs:
                    results_dict.update(job.get())
                #print("Time to execute jobs:", time.time() - start_time_test)     
                #   
                for agent in AGENTS:

                    #Update agent info
                    agent.Position = results_dict[agent.ID][0]
                    agent.Velocity = results_dict[agent.ID][1]
                    agent.Phase = results_dict[agent.ID][2]
                    agent.HueColor = results_dict[agent.ID][3]
                    agent.oscillator = results_dict[agent.ID][4]
                    color = results_dict[agent.ID][5]

                    #Prepare OSC Agent Position
                    position = agent.ScaledPosition()                
                    osc_msg_pos.add_arg(agent.ID)
                    osc_msg_pos.add_arg(int(position[0] * 1000))
                    osc_msg_pos.add_arg(int(position[1] * 1000))
                    osc_msg_pos.add_arg(int(position[2] * 1000))            

                    #Prepare OSC Agent Color                
                    osc_msg_color.add_arg(agent.ID)
                    osc_msg_color.add_arg(color)

                    #Add audio bundle
                    if USE_AUDIO:
                        audio_bundle.add_content(agent.MusicalAgent.UpdateBundle(agent.Phase, agent.oscillator, agent.ScaledVelocity()))
                
                for interactive_agent in AGENTS_interactive.values():
                    #Update agent, time in seconds
                    interactive_agent.Update(DELTA_TIME_MS / 1000.0, TOTAL_TIME_MS / 1000.0)          

                    #Prepare OSC Agent Color                
                    osc_msg_color.add_arg(interactive_agent.ID)
                    osc_msg_color.add_arg(interactive_agent.CurrentColorHex())  
            
            #Send all agents info to Unity app
            bundle.add_content(osc_msg_pos.build())
            bundle.add_content(osc_msg_color.build())
            if USE_AUDIO:
                bundle.add_content(audio_bundle.build())
            client.send(bundle.build())


            #Maintain the real-time frame rate
            elapsed_time = time.time() - start_time            
            time_to_wait = (DELTA_TIME_MS / 1000.0) - elapsed_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            actual_elapsed_time = time.time() - start_time
            TOTAL_TIME_MS += int(actual_elapsed_time * 1000.0)
            #print("Elapsed time:", elapsed_time, "Total time:", TOTAL_TIME_MS)
            #sleep delta time of this thread
            #time.sleep(DELTA_TIME_MS / 1000.0)
            #TOTAL_TIME_MS += DELTA_TIME_MS
    except KeyboardInterrupt:
        print("Terminating pool...")
    finally:
        #Force stop threads in pool
        pool.terminate()
        pool.close()
        pool.join()
        print("Pool closed.")


############# END: BEHAVIOUR #############



############# ***** MAIN PROGRAM ***** #############

if __name__ == "__main__":
    # Create the OSC server in a parallel thread
    server = osc_server.ThreadingOSCUDPServer((local_ip, local_port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server_thread = threading.Thread(target=lambda: server.serve_forever())
    server_thread.start()

    # Send the local IP and port to the Unity app for connection
    client.send_message("/connect", [local_ip, local_port])

    # Run in a parallel thread the agents behaviour
    RUNNING = True
    behaviour_thread = threading.Thread(target=lambda: Global_Behaviour(client))             
    behaviour_thread.start()

    # Run the GUI

    SGUI.SwarmalatorsGUI_Define(N, J, K, SPEED, N_interactive)

    def OnStateChangedGUI(id):
        global AGENTS
        global J
        global K
        if id == 1:
            print("Static sync")
            J = 0.1
            K = 1.0
        elif id == 2:
            print("Static async")
            J = 0.1
            K = -1.0
        elif id == 3:
            print("Static phase wave")
            J = 1.0
            K = 0.0
        elif id == 4:
            print("Splintered phase wave")
            J = 1.0
            K = -0.1
        elif id == 5:
            print("Active phase wave")
            J = 1.0
            K = -0.75
        SGUI.SwarmalatorsGUI_Set_J_K(J, K)

    SGUI.OnButtonClickedEvent = OnStateChangedGUI

    def OnKnobChangedGUI(id, value):
        global AGENTS
        global N
        global SPEED
        global J
        global K
        global client
        global N_interactive
        with lock:
            if id == 1:        
                N = int(value)
                print("N:", N)
                Instantiate_Agents(client)
            elif id == 2:
                print("J:", value)
                J = value
                for agent in AGENTS:
                    agent.J = J
            elif id == 3:
                print("K:", value)
                K = value
                for agent in AGENTS:
                    agent.K = K
            elif id == 4:
                print("Speed:", value)
                SPEED = value
                for agent in AGENTS:
                    agent.Speed = SPEED
            elif id == 5:
                print("Interactive N:", value)
                N_interactive = int(value)
                Instantiate_Interactive_Agent(client)

    SGUI.OnKnobChangedEvent = OnKnobChangedGUI

    def OnCloseWindowGUI():
        global RUNNING
        global server
        global client
        global N
        global N_interactive
        #Delete agents
        client.send_message("/agents/remove", N + N_interactive)
        #Close server
        server.shutdown()
        #Stop the behaviour thread
        RUNNING = False
        print("Closing server")    
        time.sleep(0.2)

    SGUI.OnCloseWindowEvent = OnCloseWindowGUI

    SGUI.SwarmalatorsGUI_Run()