// swarmalators.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "Swarmalator.h"
#include "MusicalSwarmalator.h"
#include "SwarmalatorsGUI.h"

#include <iostream>
#include <osc/OscOutboundPacketStream.h>
#include <osc/OscReceivedElements.h>
#include <osc/OscPacketListener.h>
#include <ip/UdpSocket.h>
#include <thread>
#include <chrono>
#include <mutex>
#include <atomic>
#include <functional>
#include <unordered_map>


//OSC LIbrary from http://www.rossbencina.com/code/oscpack
//ImGui Library from https://github.com/ocornut/imgui/wiki/Getting-Started


#define EXT_ADDRESS "127.0.0.1"
#define EXT_PORT 6011

#define LOCAL_ADDRESS "127.0.0.1"
#define LOCAL_PORT 6010

#define OUTPUT_BUFFER_SIZE 4096 * 20
#define BASE_interactive_ID 1000
#define USE_AUDIO 0

static std::atomic<bool>                                    g_Running(false);
static std::atomic<int>                                     g_N(30);
static std::atomic<int>                                     g_N_interactive(0);
static std::atomic<float>                                   g_J(1.0f);
static std::atomic<float>                                   g_K(-0.75f);
static std::atomic<float>                                   g_SPEED(3.0f);
static std::atomic<std::pair<int, std::array<float, 3>>>    g_last_interactive_position({ 0, {0.0f, 0.0f, 0.0f} });
static std::atomic<int>                                     g_last_interactive_control(0);


class ExternalPacketListener : public osc::OscPacketListener {
protected:

    virtual void ProcessMessage(const osc::ReceivedMessage& m,
        const IpEndpointName& remoteEndpoint)
    {
        (void)remoteEndpoint; // suppress unused parameter warning

        try {
            // example of parsing single messages. osc::OsckPacketListener
            // handles the bundle traversal.

            if (std::strcmp(m.AddressPattern(), "/test/alive/") == 0) {
                osc::ReceivedMessage::const_iterator arg = m.ArgumentsBegin();
                std::cout << "Connected!" << " ";
                while (arg != m.ArgumentsEnd()) {
                    if (arg->IsString())
                        std::cout << arg->AsString() << " ";
                    if (arg->IsInt32())
                        std::cout << arg->AsInt32() << " ";
                    if (arg->IsFloat())
                        std::cout << arg->AsFloat() << " ";
                    if (arg->IsBool())
                        std::cout << arg->AsBool() << " ";
                    arg++;
                }
                std::cout << std::endl;
            }
            else if (std::strcmp(m.AddressPattern(), "/agents/position/id") == 0) {
                osc::ReceivedMessage::const_iterator arg = m.ArgumentsBegin();
                int id = (arg++)->AsInt32();
                int x = (arg++)->AsInt32();
                int y = (arg++)->AsInt32();
                int z = (arg++)->AsInt32();
                
                std::cout << "Agent " << id << " at " << x << " " << y << " " << z << std::endl;
                g_last_interactive_position = std::make_pair(id, std::array<float, 3>{x / 1000.0f, y / 1000.0f, z / 1000.0f});
            }
            else if (std::strcmp(m.AddressPattern(), "/agents/control") == 0) {
                osc::ReceivedMessage::const_iterator arg = m.ArgumentsBegin();
                int id = (arg++)->AsInt32();
                int control_type = (arg++)->AsInt32();
                int control_value = (arg++)->AsInt32();  
                if (control_type == 1 && control_value == 1) {
                    g_last_interactive_control = id;
                    std::cout << "Control " << id << " " << control_type << " " << control_value << std::endl;
                }

            }
        }
        catch (osc::Exception& e) {
            // any parsing errors such as unexpected argument types, or 
            // missing arguments get thrown as exceptions.
            std::cout << "error while parsing message: "
                << m.AddressPattern() << ": " << e.what() << "\n";
        }
    }
};

void runSocket(UdpListeningReceiveSocket* socket) {
    socket->Run();
}

////////////////////////////////// INSTANTIATION //////////////////////////////////////


void Instantiate_Agents(UdpTransmitSocket* client,
    std::vector<std::unique_ptr<Swarmalator>>* AGENTS,
    std::unordered_map<int, std::unique_ptr<Swarmalator>>* AGENTS_interactive_map
    ) {

    int num_agents = g_N - AGENTS->size();
    if (num_agents == 0) {
        return;
    }

    // Create OSC bundle
    char buffer[OUTPUT_BUFFER_SIZE];
    osc::OutboundPacketStream bundle(buffer, OUTPUT_BUFFER_SIZE);
    bundle << osc::BeginBundle();

    if (num_agents > 0) {
         // Add agents
        bundle << osc::BeginMessage("/agents/instantiate/id")
            << 0 << 0; // 0: shape=sphere, 0: movMode=teleport

        //pos_msg << osc::BeginMessage("/agents/position/id");

        int last_id = AGENTS->size();
        for (int i = 0; i < num_agents; ++i) {
            int id = last_id + i + 1;

            bundle << id;
            //pos_msg << id;

            auto agent = std::make_unique<Swarmalator>(id, false);
            agent->J = g_J;
            agent->K = g_K;
            agent->Speed = g_SPEED;
            agent->AssignRandomPosition(1.0f);            

            AGENTS->push_back(move(agent));
        }
        bundle << osc::EndMessage;
        //pos_msg << osc::EndMessage;

        bundle << osc::BeginMessage("/agents/position/id");

        for (int i = last_id; i < AGENTS->size(); ++i) {
            bundle << (*AGENTS)[i]->ID;
            auto position = (*AGENTS)[i]->ScaledPosition();
            bundle << static_cast<int>(position[0] * 1000)
                << static_cast<int>(position[1] * 1000)
                << static_cast<int>(position[2] * 1000);
        }
        bundle << osc::EndMessage;

        //Add audio components
        if (USE_AUDIO) {
            for (int i = last_id; i < AGENTS->size(); ++i) {
                auto agent = (*AGENTS)[i].get();
                agent->MusicalSwarmalator.InstantiateBundleAndPlay(bundle, 3, 0.01f, 0, 0.2f, 0.2f, agent->Phase, agent->oscillator, agent->ScaledVelocity());
                //Print audio success
                //std::cout << "Audio components added " << agent->ID << std::endl;
            }
            
        }
    }
    else {
        // Remove agents
        num_agents = -num_agents;
        bundle << osc::BeginMessage("/agents/remove/id");

        for (int i = 0; i < num_agents; ++i) {
            auto agent = move(AGENTS->back());
            AGENTS->pop_back();
            bundle << agent->ID;
        }
        bundle << osc::EndMessage;
    }

    // Set others for all agents
    //iterate AGENTS

    for (const auto& agent : *AGENTS) {
        std::vector<Swarmalator*> others;
        for (const auto& other : *AGENTS) {
            if (agent.get() != other.get()) {
                others.push_back(other.get());
            }
        }
        for (auto it = AGENTS_interactive_map->begin(); it != AGENTS_interactive_map->end(); ++it) {
            others.push_back(it->second.get());
        }
        agent->SetOthers(others);
    }

    // Send the instantiation bundle
    bundle << osc::EndBundle;
    client->Send(bundle.Data(), bundle.Size());
}

void Instantiate_Interactive_Agents(UdpTransmitSocket* client,
    std::vector<std::unique_ptr<Swarmalator>>* AGENTS,
    std::unordered_map<int, std::unique_ptr<Swarmalator>>* AGENTS_interactive_map
) {

    int num_agents = g_N_interactive - AGENTS_interactive_map->size();
    if (num_agents == 0) {
        return;
    }

    // Create OSC bundle
    char buffer[OUTPUT_BUFFER_SIZE];
    osc::OutboundPacketStream bundle(buffer, OUTPUT_BUFFER_SIZE);
    bundle << osc::BeginBundle();

    if (num_agents > 0) {
         // Add agents
        bundle << osc::BeginMessage("/agents/instantiate/id")
            << 1 << 0; // 0: shape=square, 0: movMode=teleport

        int last_id = AGENTS_interactive_map->size();
        for (int i = 0; i < num_agents; ++i) {
            int id = BASE_interactive_ID + last_id + i + 1;

            bundle << id;
            //pos_msg << id;

            auto agent = std::make_unique<Swarmalator>(id, true);
            agent->J = g_J;
            agent->K = g_K;
            agent->Speed = g_SPEED;
            agent->AssignRandomPosition(1.0f);

            AGENTS_interactive_map->insert(std::make_pair(id, move(agent)));
        }
        bundle << osc::EndMessage;
        //pos_msg << osc::EndMessage;

        bundle << osc::BeginMessage("/agents/position/id");

        for (auto it = AGENTS_interactive_map->begin(); it != AGENTS_interactive_map->end(); ++it) {
            bundle << it->second->ID;
            auto position = it->second->ScaledPosition();
            bundle << static_cast<int>(position[0] * 1000)
                << static_cast<int>(position[1] * 1000)
                << static_cast<int>(position[2] * 1000);
        }
        bundle << osc::EndMessage;

        //bundle << buffer_inst << buffer_pos;

    }
    else {
        // Remove agents
        num_agents = -num_agents;
        bundle << osc::BeginMessage("/agents/remove/id");

        for (int i = 0; i < num_agents; ++i) {
            //remove interactive agent from map with the last id
            int last_id = BASE_interactive_ID + AGENTS_interactive_map->size() - i;
            AGENTS_interactive_map->erase(last_id);
            bundle << last_id;
        }
        bundle << osc::EndMessage;
    }

    // Set others for all agents
    //iterate AGENTS

    for (const auto& agent : *AGENTS) {
        std::vector<Swarmalator*> others;
        for (const auto& other : *AGENTS) {
            if (agent.get() != other.get()) {
                others.push_back(other.get());
            }
        }
        for (auto it = AGENTS_interactive_map->begin(); it != AGENTS_interactive_map->end(); ++it) {
            others.push_back(it->second.get());
        }
        agent->SetOthers(others);
    }

    // Send the instantiation bundle
    bundle << osc::EndBundle;
    client->Send(bundle.Data(), bundle.Size());
}

////////////////////////////////// GLOBAL BEHAVIOUR //////////////////////////////////////

void precise_sleep(float seconds) {
    auto start_time = std::chrono::high_resolution_clock::now();    
    auto end_time = start_time + std::chrono::duration_cast<std::chrono::high_resolution_clock::duration>(std::chrono::duration<float>(seconds));

    while (std::chrono::high_resolution_clock::now() < end_time) {
        std::this_thread::yield(); // This allows other threads to run while we wait
    }
}

//void precise_sleep(float seconds) {
//    if (seconds <= 0.0f) return; // No need to sleep for non-positive durations
//
//    auto now = std::chrono::high_resolution_clock::now();
//    auto end_time = now + std::chrono::duration_cast<std::chrono::high_resolution_clock::duration>(std::chrono::duration<float>(seconds));
//
//    // Calculate sleep duration in milliseconds
//    auto sleep_duration = static_cast<std::chrono::milliseconds::rep>(seconds * 1000) - 1;
//
//    printf("Sleeping for %d milliseconds\n", sleep_duration);
//
//    // Sleep for the main duration minus a small portion (e.g., 1 millisecond)
//    std::this_thread::sleep_for(std::chrono::milliseconds(sleep_duration));
//
//    // Spin-wait for the remaining time
//    while (std::chrono::high_resolution_clock::now() < end_time) {
//        std::this_thread::yield(); // Yield to allow other threads to run
//    }
//}

int MAIN_LOOP(UdpTransmitSocket* client,
    std::vector<std::unique_ptr<Swarmalator>>* AGENTS,
    std::unordered_map<int, std::unique_ptr<Swarmalator>>* AGENTS_interactive_map,
     std::mutex* lock) {

    //////////////// Logic Initialization ////////////////

    int DELTA_TIME_MS = 20;
    int TOTAL_TIME_MS = 0;

    Instantiate_Agents(client, AGENTS, AGENTS_interactive_map);
    Instantiate_Interactive_Agents(client, AGENTS, AGENTS_interactive_map);

    while (g_Running) {        

        //////////////////////// Logic Start Loop ////////////////////////

        auto start_time = std::chrono::high_resolution_clock::now();


        char buffer[OUTPUT_BUFFER_SIZE];
        osc::OutboundPacketStream bundle(buffer, OUTPUT_BUFFER_SIZE);
        bundle << osc::BeginBundleImmediate;

        bundle << osc::BeginMessage("/agents/position/id");

        std::unique_lock<std::mutex> lock_guard(*lock);

        //Autonomous Agents: Update and gather positions
        for (auto& agent : *AGENTS) {
            agent->Update(DELTA_TIME_MS / 1000.0f, TOTAL_TIME_MS / 1000.0f);

            auto position = agent->ScaledPosition();

            // Prepare OSC Agent Position
            bundle << agent->ID
                << static_cast<int>(std::round(position[0] * 1000))
                << static_cast<int>(std::round(position[1] * 1000))
                << static_cast<int>(std::round(position[2] * 1000));
        }

        bundle << osc::EndMessage;

        bundle << osc::BeginMessage("/agents/color/id");

        //Autonomous Agents: Gather colors
        for (auto& agent : *AGENTS) {            
            bundle << agent->ID
                << agent->CurrentColorHex().c_str();
		}

        //Interactive Agents
        auto last_interactive_position = g_last_interactive_position.load();
        if(last_interactive_position.first != 0) {
			auto it = AGENTS_interactive_map->find(last_interactive_position.first);
			if (it != AGENTS_interactive_map->end()) {
				it->second->SetFromScaledPosition(last_interactive_position.second[0], last_interactive_position.second[1], last_interactive_position.second[2]);
			}
			g_last_interactive_position = std::make_pair(0, std::array<float, 3>{0.0f, 0.0f, 0.0f});
		}
        if (g_last_interactive_control != 0) {
			auto it = AGENTS_interactive_map->find(g_last_interactive_control);
			if (it != AGENTS_interactive_map->end()) {
				it->second->ResetOscillator(TOTAL_TIME_MS / 1000.0f);
			}
			g_last_interactive_control = 0;
		}
        for (auto it = AGENTS_interactive_map->begin(); it != AGENTS_interactive_map->end(); ++it) {
            it->second->Update(DELTA_TIME_MS / 1000.0f, TOTAL_TIME_MS / 1000.0f);
			bundle << it->second->ID
				<< it->second->CurrentColorHex().c_str();
		}
        bundle << osc::EndMessage;

        // Automoust agents: Audio components
        if (USE_AUDIO) {
			for (auto& agent : *AGENTS) {
				agent->MusicalSwarmalator.UpdateBundle(bundle, agent->Phase, agent->oscillator, agent->ScaledVelocity());
			}
		}

        lock_guard.unlock();
        

        bundle << osc::EndBundle;
        client->Send(bundle.Data(), bundle.Size());
        bundle.Clear();

        //////////////////////// Logic End Loop ////////////////////////       

        //////////////////////// Time Calculation ////////////////////////

        // Wait for the next update
        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<float> elapsed_time = end_time - start_time;

        float time_to_wait = (DELTA_TIME_MS / 1000.0f) - elapsed_time.count();
        if (time_to_wait > 0) {
            precise_sleep(time_to_wait);
            //Print time to wait
            //std::cout << "Time to wait: " << time_to_wait << std::endl;            
        }
        auto end_time_2 = std::chrono::high_resolution_clock::now();
        std::chrono::duration<float> elapsed_time_2 = end_time_2 - start_time;
        TOTAL_TIME_MS += int(elapsed_time_2.count() * 1000.0f);
        //print total time
        //std::cout << "Total time: " << TOTAL_TIME_MS << ", " << elapsed_time.count() << ", " << time_to_wait << ", " << elapsed_time_2.count() << std::endl;
    }

    return 0;
}



int main()
{
    UdpTransmitSocket transmitSocket(IpEndpointName(EXT_ADDRESS, EXT_PORT));

    char buffer[OUTPUT_BUFFER_SIZE];
    osc::OutboundPacketStream p(buffer, OUTPUT_BUFFER_SIZE);

    p << osc::BeginMessage("/connect") << LOCAL_ADDRESS << LOCAL_PORT << osc::EndMessage;

    transmitSocket.Send(p.Data(), p.Size());
    p.Clear();

    std::cout << "Connecting..." << std::endl;

    ExternalPacketListener listener;
    UdpListeningReceiveSocket receiveSocket(
        IpEndpointName(IpEndpointName::ANY_ADDRESS, LOCAL_PORT),
        &listener);

    // Run the socket listener in a separate thread
    std::thread socketThread(runSocket, &receiveSocket);
    

    //Sleep 1 sec
    std::this_thread::sleep_for(std::chrono::seconds(1));

    //Init parameters
    g_N = 20;    
    g_J = 1.0;
    g_K = -0.75;
    g_SPEED = 3.0;
    std::vector<std::unique_ptr<Swarmalator>> AGENTS;


    g_N_interactive = 0;
    std::unordered_map<int, std::unique_ptr<Swarmalator>> AGENTS_interactive_map;


    g_Running = true;

    //Execute agent behaviour in a separate thread
    std::mutex lock;
    std::thread globalBehaviourThread(MAIN_LOOP, &transmitSocket,&AGENTS, &AGENTS_interactive_map, &lock);

    //Event for receiving params from GUI
    auto onKnobChanged = [&transmitSocket, &AGENTS, &AGENTS_interactive_map, &lock](int id, float value)
        {
            std::unique_lock<std::mutex> lock_guard(lock);
            switch (id)
            {
            case 1://N
                g_N = static_cast<int>(value);
                std::cout << "N: " << g_N << std::endl;
                Instantiate_Agents(&transmitSocket, &AGENTS, &AGENTS_interactive_map);
                break;
            case 2://J
                std::cout << "J: " << value << std::endl;
                g_J = value;
                for (auto& agent : AGENTS) {
                	agent->J = value;
                }
                break;
            case 3://K
                std::cout << "K: " << value << std::endl;
                g_K = value;
                for (auto& agent : AGENTS) {
					agent->K = value;
				}
                break;
            case 4://Speed
                std::cout << "Speed: " << value << std::endl;
                g_SPEED = value;
                for (auto& agent : AGENTS) {
                    agent->Speed = value;
                }
                break;
            case 5://N_interactive
                g_N_interactive = static_cast<int>(value);
                std::cout << "N_interactive: " << g_N_interactive << std::endl;
                Instantiate_Interactive_Agents(&transmitSocket, &AGENTS, &AGENTS_interactive_map);
                break;
            default:
                break;
            }
        };
    SetOnKnobChangedEvent(std::function<void(int, float)>(onKnobChanged));
    

    //Execute GUI in a separate thread
    std::thread guiThread(SwarmalatorsGUI_Run, g_N.load(), g_J.load(), g_K.load(), g_SPEED.load(), g_N_interactive.load());

    //Event for closing window
    auto FinishAll = [&receiveSocket, &socketThread, &globalBehaviourThread, &guiThread]()
        {
            // Implement logic to run when the window is closed
            std::cout << "Close Window event!!!" << std::endl;
            g_Running = false;
        };
    SetOnCloseWindowEvent(std::function<void()>(FinishAll));


    // Main loop while running
    while (g_Running){
        //sleep 1 sec
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    // Finishing all
    p << osc::BeginMessage("/agents/remove") << g_N + g_N_interactive << osc::EndMessage;
    transmitSocket.Send(p.Data(), p.Size());
    p.Clear();
    receiveSocket.AsynchronousBreak();
    // Wait for threads to finish
    socketThread.join();
    std::cout << "Socket thread joined" << std::endl;
    globalBehaviourThread.join();
    std::cout << "Global behaviour thread joined" << std::endl;
    guiThread.join();
    std::cout << "GUI thread joined" << std::endl;
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu
