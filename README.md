# Human-Swarm Systems' Examples

These examples use a software for visualization and interaction of simple 3D elements that can communicate with external applications through OSC messages. We called the **Human-Swarm Interactive Music System App (HS-ims app)**. It is intended for multi-agent systems with a user interaction focus, especially for sound and music applications. It only supports Windows and Mac OS. You can download the executables for each OS from:

* [HS-ims Windows](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/win_ims.zip)

* [HS-ims Mac](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/mac_ims.zip)

There is not installation process, this application can be opened directly.

This repository contains examples that use this **HS-ims app** considering three programming languages; [Python](https://www.python.org/), [C++](https://cplusplus.com/), and [Max 8](https://cycling74.com/products/max). However, as you can communicate with the **HS-ims app** through [OSC](https://ccrma.stanford.edu/groups/osc/index.html) messages, you can use any software that supports standard UDP communication and create you own interactive swarm system. With that in mind, we are going to describe first the **HS-ims app**, then *how to run the examples*, and the *OSC API* for the **HS-ims app** if you want to create your own applications.



## 1. The **Human-Swarm Interactive Music System App (HS-ims app)**

### 1.1. Description

This software is intended for research conducted in multi-agent systems for sound and music applications that have a user interaction component, considered mainly for studying swarm intelligence and self-synchronization strategies. Moreover, it can be known as an *artifact* to perform experimentation.

It is implemented in the [Unity](https://unity.com/) game engine since the intention is to reach several platforms including mobile and XR. So far, we have this version for Windows and Mac PCs. The software is still under development and the code will be released in the future. 

This app serves mainly for three purposes: 
**visualization**, **human interaction**, and **data collection** regarding objects that moves in a virtual 3D space. In the image below you can visualize this 3D environment where you can navigate using the scroll, center, and right mouse button.  You can find the following components in this screenshot: two objects instantiated externally, a cyan sphere and a cube; a 3D head model enclosed in a cube, which is the *audio listener* reference; and a user interface with few options explained later. 

![hs-ims-main-iterface](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main/docs/imgs/hs-ims-main-iterface.png)

The two cyan objects were created by another software (let's call it *X app*) that sent the corresponding OSC messages to instantiate and place them in an specific (x, y, z) point. Both objects can be clicked (left or right button in the mouse) and only the cube can be moved in the plane of its faces using the mouse, these interactions can be sent back to *X app* if needed, which allows a two-way communication. As OSC messages are based on UDP, the **HS-ims app** and *X app* can reside in different machines connected through the network. We are exemplifying in this repository this two-way communication with the three programming languages used in the examples ([Python](https://www.python.org/), [C++](https://cplusplus.com/), and [Max 8](https://cycling74.com/products/max). At the end, we are going to describe the OSC API that allows you to use the **HS-ims app** and understand the examples in this repository.

The *audio listener* object can be moved as the cyan cube and is able to change the spatial audio reference when we are synthesizing sound through the app.

The user interface on top left can be shown by clicking the button `CONFIG` (in the image above the button is not there since it was already clicked). There are few configuration options, which are:

* `My IP`: It shows the IP address where the app is running, which must be know if we are sending OSC messages from an external machine.

* `Local Port`: It is the port used for incoming OSC messages. You can change the default value if needed.

* `Center Camera`: Press it to place the virtual camera at the default position.

* `Center Listener`: Press it to place the *audio listener* in the center of the coordinate system.

* `Remove All`: Remove all the agents in the virtual world.

* `Show Listener Always`: Show or hide the *audio listener* 3D object.

* `Show Agents IDs`: Show or hide a white label in an agent that denotes its ID number. 

* `File Path`: Write here the directory where the system will save files from data collection.

* `Check File Path`: Press this button to verify that the `File Path` exist. You should see a message regarding this inquiry to the left of this button.

* `Start`: Start the data collection process and file recording.

* `Stop`: Stop the data collection process and file recording.

* `Save and Close`: Save the settings that you change in this panel and close it.

Additionally, when you connected an external client via OSC messages, you can see the IP address of this remote client in the bottom left of the window.



### 1.2. Basic Interface

## 2. How to run the examples

We assume that you have a basic knowledge of the programming languages listed below and a working environment in your machine for the ones that you are interested in. These examples has been tested on Windows, but they should work on Mac OS with particular considerations (specially for the C++ example).

Previous to run the examples, open the **HS-ims app** according to your OS (You can download it from the links above or [here](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/tag/v1.0.0))

<!--..... open the **HS-ims app** for all, these were implemented  and tested in windows, so find a way to work with max) -->

### 2.1. MAX

We used [Max](https://cycling74.com/products/max) version 8.6.4.

### 2.2. Python

### 2.3. C++

...

## 3. HS-ims app: OSC API Documentation

  Before delving into the specific OSC messages, it's important to understand the enum parameters used throughout the API. When we refer to these parameters, you can use the corresponding number. Then, we will show tables that categorize and condense the OSC messages based on their direction of communication (incoming to the application and outgoing from the application), as well as by their relevant modules (Agent, Boundary, Environment, Audio, and Recording). Note that some messages can have optional parameters with default values (e.g. for `/agents/instantiate` we have three parameters,  `N [shape=0]  [movMode=0]`, where `shape` and `movMode` are optional with default values `0` and `0` correspondingly.)

### 3.1. Enum definitions

- **shape**\
  Represents the type of agent in terms of 3D shape:

  `0`: *Sphere*\
  `1`: *Cube*\
  `2`: *Pyramid*

- **movMode**\
  Specifies the movement mode of an agent:

  `0`: *Teleport* <sub>The agent with this mode will move instantaneously to an (x, y, z) position assigned.</sub>\
  `1`: *Follow* <sub>The agent will mode towards an (x, y, z) positions with certain speed.</sub>\
  `2`: *Velocity* <sub>The agent will move with a velocity vector (vx, vy, vz). Remember that the velocity vector denote direction and speed.</sub>

- **initPosMode**\
  Initial mode for place agents when they are added (see `/agents/add`):

  `0`: *Origin* <sub>Place the agents at point (0, 0, 0)</sub>\
  `1`: *Random* <sub>Place the agents around a radius randomly </sub>\
  `2`: *Explicit* <sub>Place the agents in explicit (x, y, z) positions, adding as many set of coordinates as agents to add </sub>

- **color_action**\
  Specifies agents will be colored:

  `0`: *Random color assignment*\
  `1`: *Assign specified color*

- **show_feedback**\
Determine whether the feedback for the local communication radius is shown (see `/agents/localcomm`):

    `0`: *No*\
    `1`: *Yes*  

- **boundary_type**
Specifies the world boundary shape to manage (see `/boundary/add/id` and `/boundary/scale/id`):

  `0`: *Sphere*\
  `1`: *Cube*

- **cc_id**
Specifies the audio synthesizer ID parameter to modify. Depending of the parameter, its `value` could be particular.(See `Audio Module` later below):

  `0`: *Oscillator type* <sub>The oscillator type for sound generation. The possible options (which should be provided in the `value`) are: </sub>
    > `0`: *Sine*\
    > `1`: *Square*\
    > `2`: *Saw*\
    > `3`: *Triangle*

  `2`: *Frequency* <sub>The sound frequency for the oscillator of a synthesizer in Hz</sub>\
  `16`: *Gain* <sub>The amplitude gain for the oscillator of a synthesizer. `value` between 0.0 and 1.0</sub>\
  `82`: *Amp_env_attack* <sub> Attack time for the amplitude envelop of a synthesizer in seconds.</sub>\
  `83`: *Amp_env_decay* <sub> Decay time for the amplitude envelop of a synthesizer in seconds.</sub>\
  `85`: *Amp_env_sustain* <sub> Sustain level for the amplitude envelop of a synthesizer.`value` between 0.0 and 1.0</sub>\
  `17`: *Amp_env_release* <sub> Release time for the amplitude envelop of a synthesizer in seconds.</sub>\
  `93`: *Low Pass Filter - Cut Off Frequency* <sub> `value` in Hz.</sub>\
  `18`: *Low Pass Filter - Resonance(Q)* <sub> `value` between 0 and 1.0</sub>\
  `19`: *Reverb - Room* <sub> `value` between -10000.0 and 0.0 (from less to more reverb effect)</sub>

- **control_type**\
 Specifies the code for a control type when an action is performed over an agent (see `/agents/control`):

  `0`: *Left mouse click*\
  `1`: *Right mouse click*

- **control_value**\
 Specifies the value for a control when an action is performed over an agent (see `/agents/control`):

  `0`: *Release*\
  `1`: *Press*

- **event_type**\
  Specifies the type of boundary event (see `/boundary/event/id`):

  `0`: *Enter boundary*\
  `1`: *Exit boundary*

  ## 3.2. Incoming OSC Messages

  ### Network Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Connect client | `/connect` | `local_ip  local_port`| Request a connection with the app and share the `local_ip` and  `local_port` of the machine that you want to communicate with the app. If you are using the same machine, you can use `127.0.0.1` as `local_ip`. | `/connect 192.0.0.3 6010` (Connect from a machine with ip=192.0.0.3 willing to receive data on port 6010)|

  ### Agent Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Instantiate Agents | `/agents/instantiate` | `N [shape=0]  [movMode=0]`| Instantiate agents in point (0,0,0) with specified properties. IDs are assigned in order depending on existing agents. | `/agents/instantiate 10 1 2` (Instantiate 10 cube agents with velocity movement mode)|
| Instantiate Agents By ID | `/agents/instantiate/id` | `shape movMode id0 id1 id2...` | Instantiate specified agents by ID. It will create as many agents as IDs | `/agents/instantiate/id 1 0 1 3 100 501` (Instantiate 4 cube agents with teleport movement mode. Each with IDs 1, 3, 100, and 501 correspondingly.) |
| Add Agents | `/agents/add` | `N [shape=0] [movMode=0] [initPosMode] [spawning_radius if initPosMode = 1] [ x0 y0 z0 x1 y1 z1... if  initPosMode = 2]` | Add agents with position options. | `/agents/add 3 2 1 2 100 20 10 230 -20 113 24 112 -115` (Add 3 pyramid agents in Follow movement mode in the explicit positions (100, 20, 10), (230, -20, 113), and (24, 112, -115) respectively.) |
| Remove Agents | `/agents/remove` | `N [shape=-1] [movMode=-1]` | Remove the N last agents created. `shape` or/and `movMode` can be used as filters if needed (-1 means all). | `/agents/remove 5 1 1` (Remove the last 5 cube agents in Follow movement mode. )|
| Remove Agents By ID | `/agents/remove/id` | `id0 id1 id2...` | Remove specified agents by ID.| `/agents/remove/id 2 50 43` (Remove 3 agents with IDs 2, 50 and 43.)|
| Update Agent Position By ID | `/agents/position/id` | `id0 x0 y0 z0 id1 x1 y1 z1...` | Update positions (In millimeters) for specified agents by ID. In teleport mode the agent will be placed immediately, in Follow mode the agent will go to this position, and in Velocity it will set the velocity vector.  | `/agents/position/id 2 100 -30 -56 23 200 -301 21 12 -200 -500 125` (Set positions for agents 2, 23 and 12 at (100, -30, -56), (200, -301, 21), and (-200, -500, 125) respectively.) |
| Update Agent Speed By ID | `/agents/speed/id`| `id0 speed0 id1 speed1 ...` | Update speeds for specified agents by ID (in mm/s). The agents must be in Follow or Velocity mode | `/agents/speed/id 3 100 6 350` (Speed for agent 3 is set to 100 mm/s and for agent 6 to 350 mm/s)|
| Update Agent Direction By ID | `/agents/direction/id` | `id0 dx0 dy0 dz0 id1 dx1 dy1 dz1...` | Update move directions for specified agents by ID. The directional vectors will be normalized if they are not. Agents must be in Follow or Velocity mode. Be aware that, if using this, you need to provide a speed to apply motion (see `/agents/speed/id`) | `/agents/direction/id 3 1 0 0 7 0 -1 0` (Agent 3 is set to move along the positive X axis, while agent 7 will move along the negative Y axis.) |
| Update Agent Velocity By ID | `/agents/velocity/id` | `id0 vx0 vy0 vz0 id0 vx0 vy0 vz0 ...` | Update velocities for specified agents by ID (in mm/s). The velocity vectors provide speed and direction. | `/agents/velocity/id 3 0 102 0 7 0 0 -210` (Agent 3 will move along the positive Y axis at 102 mm/s and agent 7 along the negative Z axis at 210 mm/s.)|
| Color Agents | `/agents/color`| `N [shape=-1] [color_action] [color0 color1... if color_action=1]` | Change colors of agents with specified properties. If on N is provided, then all colors will be assigned randomly, which is the same effect as using `N -1 0`. If  `color_action=1`, explicit colors can be provide in a string of hex format (e.g. 000000 is black, 111111 is white, 00ff00 is green, etc.) | `/agents/color 2 0 1 00ff00 ff0000` (Assign to 2 sphere agents the green and red color) |
| Color Agents By ID | `/agents/color/id` | `id0 color0 id1 color1...` | Change colors (in hex format) of specified agents by ID. | `/agents/color 5 00ff00 12 ff0000` (Assign green to agent 5 and red to agent 12.) |
| Set Agent Radius By ID | `/agents/radius/id` | `id0 radius0 alpha0 color0 id1 radius1 alpha1 color1...` | Shows a semitransparent sphere around of agents by ID. The radius (in mm), the color, and the transparency factor (alpha in the range[0, 1]) have to be provided per agent. | `/agents/radius/id 2 2000 0.5 00ff00 7 1500 0.75 ff0000` (Shows a green sphere of radius 2000 mm surrounding agent 2 with 50% of transparency, and for agent 7 one red with 1500 mm of radius with 75% of transparency.) |
| Configure Local Communication       | `/agents/localcomm` | `maxCommunicationRange(mm) communicationLatency(ms) show_feedback` | Configure local agent communication settings. If `show_feedback=1` you can visualize a semitransparent sphere coming out of the agent until reaching a radius(`maxCommunicationRange(mm)`) in an specific time (`communicationLatency(ms)`). This is the local communication mechanism for all agents. |
| Send Local Communication Messages   | `/agents/localcomm/send` | `id0 msg0 id1 msg1 ...`| Send local communication messages between agents. All specified agents will broadcast a message that will reach other agents according to the configuration provided by `/agents/localcomm`. The `msg` is a string. | `/agents/localcomm/send 10 "hello" 23 "world"` (Agents 10 and 23 will send a local message, 10 will send "hello" and 23 the string "world".) |

### Boundary Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Add Boundary | `/boundary/add/id` | `id boundary_type x y z (radius if boundary_type = 0, scale_x scale_y scale_z if boundary_type = 1) alpha color_hex` | Add a new boundary with specified properties. |  `/boundary/add/id 21 0 100 -20 -125 10000 0.30 00ff00` (Add a green sphere boundary of radius 10000 mm with ID = 21 at 30% transparency in the point (100, -20, -125). `/boundary/add/id 21 1 100 -20 -125 100 200 300 0.30 00ff00` (A similar boundary but this time is a cubic object with dimensions x=100mm(large) y=200mm(height) and z=300(depth)))|
| Remove Boundary | `/boundary/remove/id`  | `id` | Remove one specified boundary by ID. | `/boundary/remove/id 3` (Remove boundary with ID 3)|
| Update Boundary Position By ID | `/boundary/position/id` | `id x y z` | Update position (in mm) for an specific boundary by ID. | `/boundary/position/id 3 200 -300 -500` (Set boundary position with ID 3 at (200, -300, -500)) |
| Update Boundary Scale By ID | `/boundary/scale/id` | `id (radius if boundary_type = 0, scale_x scale_y scale_z if boundary_type = 1)` | Update scale or radius for specified boundaries by ID.  | `/boundary/scale/id 21 2000` (Change the scale for a sphere boundary of ID = 21 to 2000 mm)|
| Update Boundary Transparency By ID  | `/boundary/alpha/id` | `id alpha`  | Update the transparency for specified boundaries by ID.  | `/boundary/alpha/id 3 0.45` (Set the transparency for boundary 3 at 45%)|
| Update Boundary Color By ID | `/boundary/color/id` | `id color`| Update the color for specified boundaries by ID. | `/boundary/color/id 2 00ff00` (Change the color for boundary 2 to green) |

### Environment Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Update or Create a 3D Arrow (only one exist in the world so far) | `/arrow` | `x y z dx dy dz scale`  | Update or create an arrow at a position (x, y, z) with a direction (dx, dy, dz) and a scale. All in mm.  | `/arrow 100 200 -400 0 0 -1 2000` (Create a 3D arrow at (100, 200, -400) point at in the same direction of the negative Z axis with a size of 2000 mm) |
| Remove Arrow | `/arrow/remove` |   Remove the arrow if it exist in the world.   | `/arrow/remove`|

### Audio Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Add Audio Synthesizer | `/agents/audio/synth/add`| `N [shape=-1] [movMode=-1]` | Add and audio synthesizer to the N first agents created. `shape` or/and `movMode` can be used as filters if needed (-1 means all). | `/agents/audio/synth/add 5 1 1` (Add an audio synthesizer component to 5 cube agents in Follow movement mode. )|
| Add Audio Synthesizer By ID | `/agents/audio/synth/add/id`| `id0 id1 id2...` | Add audio synthesizers to specified agents by ID. | `/agents/audio/synth/add/id 3 5 19` (Add audio synthesizers to agents 3, 5 and 19) |
| Remove Audio Synthesizers | `/agents/audio/synth/remove`| `N [shape=-1] [movMode=-1]` | Remove audio synthesizers from the N first agents created. `shape` or/and `movMode` can be used as filters if needed (-1 means all). | `/agents/audio/synth/remove 3 5 19` (Remove audio synthesizers from agents 3, 5 and 19) |
| Remove Audio Synthesizers By ID | `/agents/audio/synth/remove/id`| `id0 id1 id2...` | Remove audio synthesizers from specified agents by ID. | `/agents/audio/synth/remove/id 3 5 19` (Remove audio synthesizers to agents 3, 5 and 19) |
| Set Audio Synth Parameter Value | `/agents/audio/synth/param_val` | `agent_id bank cc_id value` | Set the `value` for a synthesizer parameter identified with `cc_id`  for agent with ID =`agent_id` within a `bank` (always zero for now). See `cc_id` in the enum definitions to target specific parameters | `/agents/audio/synth/param_val 3 0 93 500` (Set the cut off frequency of a low pass filter for agent 3 to 500 Hz)
| Set Audio Synth MIDI Parameter | `/agents/audio/synth/param_midi` | `agent_id bank cc_id midi_value`  | As the previous message, but instead of providing the actual value for a parameter, we give an integer number between 0 and 127, being a standard MIDI range. Depending of the parameter, this range will map to its minimum and maximum value.| `/agents/audio/synth/param_midi 3 0 18 64` (Set the resonance (Q) of a low pass filter for agent 3 to 0.5)|
| Send Audio Synth Note | `/agents/audio/synth/note` | `agent_id bank note velocity` | Send a MIDI note command the audio synthesizer of an agent with ID=`agent_id`. If `velocity` is zero this is a `note off`, and a `note on` otherwise. `bank` is always zero for now and `velocity` different from zero do not affect the gain yet, only trigger the note. | `/agents/audio/synth/note 3 0 69 64` (Send a `note on` message for agent 3 to play A4 note (440 Hz) with a velocity of 64.)) |
| Flush Audio Synth| `/agents/audio/synth/flush`| `agent_id bank` | Flush the audio synthesizer (release hanging notes) for agent with ID = `agent_id`. `bank` is always zero for now. | `/agents/audio/synth/flush 3 0` (Flush the synthesizer for agent 3) |
| Set Audio Listener Position| `/audio/listener/position` | `x y z`  | Set the position for the audio listener (if visualized, this is a 3D head enclose in cube) to an specific place (in mm) to perceive spatial audio from that point. | `/audio/listener/position 100 200 -300` (Set the audio listener to the position (100, 200, -300)) |

### Recording Module for OSC messages (Incoming and Outgoing)

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Start Recording | `/recorder/start`| `file_path` | Begin a recording session, saving to the specified path.  | `/recorder/start c:\\files` (Start a recording session a save the result in "c:\\files")
| Stop Recording | `/recorder/stop` | | Stop the current recording session. | `/recorder/stop` (Stop the recording session)
| Request Time | `/time`| | Request the current time that is running from the starting of the **HS-ims app** in milliseconds.  | `/time` (Request the current time in ms) |

## 3.3. Outgoing OSC Messages

 ### Network Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Report Client Connection | `/test/alive/` | `local_ip  local_port OK`| Report a connection with the app and share the `local_ip` and  `local_port` of the machine that you want to communicate with the app. If you are using the same machine, you will receive `127.0.0.1` as `local_ip`. | `/test/alive/ 192.0.0.3 6010 OK` (Report a connection to a machine with ip=192.0.0.3 willing to receive data on port 6010, so this machine should receive this message)|

### Agent Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Report Agent Position By ID | `/agents/position/id`| `id0 x0 y0 z0 id1 x1 y1 z1...` | Report agents' positions (in mm) by ID. For now, only cube agents can report position when they are moved in the **HS-ims app**. As we use the mouse pointer, you can expect only one agent. | `/agents/position/id 1000 100 -230 60` (Position from agent 1000 at (100, -230, 60)) |
| Report Agent Control | `/agents/control` | `agent_id control_type control_value` | Report a control action (mouse clicks for now) over an agent. | `/agents/control 5 1 1` (Report the `press` action of the right mouse click over agent 5) |
| Receive Local Communication Messages| `/agents/localcomm/recv` | `id_receiver0 id_sender0 msg0 id_receiver1 id_sender1 msg1...` | Receive local communication messages intended for specific agents. When a agent receive a local packet, this is reported through this message, in some cases, several agents can receive a message at the same time, if so, we can collect these messages at once.  | `/agents/localcomm/recv 3 1 "hello" 5 2 "bye"` (Two agents, 3 and 5, receive a local message at the same time from agents 1 and 2 respectively. Agents 3 received "hello" and agent 5 received "bye")|

### Boundary Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Report Boundary Event | `/boundary/event/id` | `agent_id boundary_id event_type` | Notify about agent's interaction with a boundary. | `/boundary/event/id 12 3 0` (Notify that agent 12 entered to boundary 3) |

### Audio Module

| Description | Address | Parameters | Usage | Examples |
|---|---|---|---|---|
| Report Audio Listener Position | `/audio/listener/position` | `x y z` |Report the position for the audio listener (if visualized, this is a 3D head enclose in cube) in an specific place (in mm) to perceive spatial audio from that point. This is reported only when it is moved with the mouse pointer. | `/audio/listener/position 100 200 -300` (Report the audio listener position (100, 200, -300)) |


