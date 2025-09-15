# SysMus25 Workshop - Human-Swarm Interactive Music Systems: Implementation and data analysis using Python

**By: [Pedro Lucas](https://www.mn.uio.no/ifi/english/people/aca/pedroplu/)**

**Please, fill this form before the workshop: https://nettskjema.no/a/527873**

In this repository, you will find the materials necessary for the workshop taking place at [SysMus25](https://www.uio.no/ritmo/english/news-and-events/events/conferences/2025/sysmus25/). The aim of this workshop is to provide fundamental concepts regarding [*human-swarm interactive music systems*](https://www.duo.uio.no/handle/10852/116392), as well as considerations for their design, implementation, and data analysis. The set of examples provided here serves as an explanatory artifact to support this goal. You can further develop the code and construct your own system based on it, or create a new system considering the information shared in the workshop.

As the emphasis shifts more towards the concepts and abstractions behind this topic illustrated in the code example, it is acceptable for you to attend without setting up this environment. However, it would be ideal for you to experience how these types of systems work on your machine. In that regard, please follow this document to ensure that you can run the examples **BEFORE** the workshop. If you encounter any issues, you can contact me at the corresponding [Discord channel](https://discord.com/channels/1380190323711414304/1380480825778503801) from the [SysMus25 server](https://discord.gg/Ja8JDhXC):


## Requirements

### Desirable Skills

* Basic Python programming knowledge.
* Not required but nice to have: 
    * Use of Jupyter Notebooks (Python-based)
    * 3D math.


### Hardware

* A laptop running Windows or MacOS.
* Try to use an external mouse instead of the mousepad for a better navigation in the virtual environment.
* Headphones so that you can hear the binaural output clearly.

### Software

* Download the **HS-ims** application for visualization and interaction in a 3D environment according to your operative system:

    * [HS-ims Windows](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/win_ims.zip) (Unzip the file and open the *Human Swarm IMS.exe* file to check that the app is working)

    * [HS-ims Mac](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/mac_ims.zip) (Unzip the file and open the .app file)
    
    > MacOS users may encounter issues when attempting to open this app. In this case, open a terminal and run the command `xattr -rc [PATH_TO_APP]` then try to open the app again. In case it still does not allow you to open the app, try the following:
        
    * Open a terminal and navigate to the following path:

        `cd <DOWNLOAD_PATH>/mac_ims.app/Contents/MacOS`

    * Once in this address, execute the following command:
    
        `chmod -R 777 "Human Swarm IMS"`

    * Now you should be able to open the app.


* For the system part: Install [Python](https://www.python.org/downloads/) >= 3.11.5 with the following packages:
    * [numpy](https://pypi.org/project/numpy/)
    * [python-osc](https://pypi.org/project/python-osc/)

* For the data analysis part: Install an environment that allows you to use [Jupyter Notebooks](https://jupyter.org/) (Based also on Python)

* **Optional:** You can use the IDE of your preference, but in this workshop I will illustrate and run the examples through [Visual Studio Code](https://code.visualstudio.com/).


## Running the Examples

1. Download this repository in your machine: https://github.com/pedro-lucas-bravo/human_swarm_examples. For this workshop, you will only need the content found in the folder **<DOWNLOAD_PATH>\human_swarm_examples\python\sysmus25_workshop**

2. Open the **HS-ims** app as mentioned in the previous section.

3. Inside **/sysmus25_workshop** you will find the folder **/HS_systems** with two examples:
    * [/template](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main/python/sysmus25_workshop/HS_systems/template): Contains some basic blocks to implement a human-swarm music system.
    * [/musical_encounters](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main/python/sysmus25_workshop/HS_systems/musical_encounters): It is based on the **/template** and contains additional elements. This is the one that will be explained in the workshop.

    In any of these folders you will find the script `main.py`. Run first the one inside **/template**. A way to do this is opening a terminal, navigate to the folder **/template** and execute the corresponding command. The following is an example using PowerShell in Windows:


    ```lang-sh
    <DOWNLOAD_PATH>\human_swarm_examples\python\sysmus25_workshop\HS_systems\template> python .\main.py
    ```

    You will be prompt the following:

    ```lang-sh
    Serving on ('127.0.0.1', 6010)
    Enter a command: 
    ```

    **Reduce considerably the sound volume of your machine before running, since it can be too noisy**. Then, write `run` to start the system. E.g:

    ```lang-sh
    Serving on ('127.0.0.1', 6010)
    Enter a command: run
    ```

    You must be able to see in the **HS-ims** app something similar to the image below, and hear constantly pitch changing sounds.

    ![template](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/docs/imgs/template_img.png)

    You can stop everything by writing `exit` in the console, which will terminate the Python script.

    You can do the same for **musical_encounters** by navigating in the corresponding folder and executing the `main.py` script. In that case, you must observe in the app something like the next image, together with reverberated punctual musical sounds.

    ![musical_encounters](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/docs/imgs/musical_encounters.jpeg)

    Again, you can stop by writing `exit` in the console. You can alternatively kill the terminal and close the **HS-ims** app.

At this point you are ready for the workshop, where more details will be provided. However, you can try some features that you will find in every example as described below.

### Example: HS_systems/template

If you run successfully this example, you are also able to perform real-time changes in the behavior of the agents in the following way:

* **Agents' speed:** You can make the agents to move faster or slower considering a multiplying factor. To do this, once you run the `main.py`, start the system with `run`, then use `v [factor]` to change the speed. E.g. for agents 1.5 times faster:

    ```lang-sh
    Serving on ('127.0.0.1', 6010)
    Enter a command: run
    Enter a command: v 1.5
    All agents speed factor set to: 1.5
    ```

### Example: HS_systems/musical_encounters

This example contains more elements and interactive options. As the **/template** example, you can change the agents' speed in the same way with  `v [factor]`. Additionally, you have the following options: **[Ensure first to start the system with the `run` command after executing the `main.py` script]**

* **Detection radius:** The surrounding semitransparent sphere that envelopes an agent is a detection radius that allows to detect nearby agents. You can change this property for all agents by using `r [radius in millimeters]`. E.g. for a 10 meter radius:

    ```lang-sh
    Enter a command: r 10000
    All agents radius set to: 10000.0
    ```

* **Instantiation:** You can add more agents to the environment by using the following commands:

    * `ia [N]`: Create additional N autonomous agents (sphere shape). E.g.
        ```lang-sh
        Enter a command: ia 3   
        Instantiated 3 agents
        ```
    * `iu [N]`: Create additional N user-controlled agents (cube shape). E.g.
        ```lang-sh
        Enter a command: iu 2   
        Instantiated 2 agents
        ```
* **Deletion:** You can remove or delete agents from the environment by using the following commands:

    * `da [N]`: Remove N autonomous agents (sphere shape) from the environment. E.g.
        ```lang-sh
        Enter a command: da 5
        Removed 5 agents
        ```
    * `du [N]`: Remove N user-controlled agents (cube shape) from the environment. E.g.
        ```lang-sh
        Enter a command: du 3
        Removed 3 agents
        ```
* **Data collection experiments:** If you run the command `experiment`, you will start to run 5 sessions that last 60 seconds each, generating one file per experiment. If you want to try this, you have to set the directory where you want these files to be saved. In that case, in the **HS-ims** app, go to `CONFIG` and change the `File Path` with your directory, then `Save and Close`. Afterwards, run the command `experiment` and wait for the experiments to finish. Your console would look like this after completing this process:

    ```lang-sh
    Enter a command: experiment
    Running experiment with 2 autonomous agents
    Experiment with 2 autonomous agents completed
    Running experiment with 4 autonomous agents
    Experiment with 4 autonomous agents completed
    Running experiment with 8 autonomous agents
    Experiment with 8 autonomous agents completed
    Running experiment with 16 autonomous agents
    Experiment with 16 autonomous agents completed
    Running experiment with 32 autonomous agents
    Experiment with 32 autonomous agents completed
    All experiments completed.
    ```
Check the directory that you chose and there you will find files with a date and timestamp of their generation. Consequently you can use these new files for trying the data analysis example, but you need to move these files to the corresponding folder and change their names in the code. You can have some related details below.

## Data Analysis

In the workshop, we will show how to collect data from the **HS-ims** app in connection with the controller developed in an external programming language, in our particular case from Python. 

To demonstrate how this data can be processed and analyzed, we will use files that were previously recorded. As such, if you want to run the data analysis example, you must download these files from here:

https://doi.org/10.5281/zenodo.15602366

Unzip the downloaded file, take the only folder you find there (**/data** folder) and put it under **<DOWNLOAD_PATH>\human_swarm_examples\python\sysmus25_workshop\data_analysis**. Your local directory for your **/sysmus25_workshop/data_analysis** folder should look like this:

```shell
\---[folder]sysmus25_workshop
|   \---[folder]data_analysis
|   |   \---[folder]data
|   |   |   \---[folder]number_of_agents
|   |   |   |       [file]ims_2025-06-04_11-17-56.csv
|   |   |   |       [file]ims_2025-06-04_11-18-58.csv
|   |   |   |       [file]ims_2025-06-04_11-20-00.csv
|   |   |   |       [file]ims_2025-06-04_11-21-02.csv
|   |   |   |       [file]ims_2025-06-04_11-22-04.csv
|   |   |   \---[folder]user_influence
|   |   |   |       [file]example_1_recording.mp4
|   |   |   |       [file]ims_2025-06-05_12-12-00.csv
|   |   [file]data_analysis_musical_encounters.ipynb
```

After having these files, you can run the Jupyter Notebook [data_analysis_musical_encounters.ipynb](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/python/sysmus25_workshop/data_analysis/data_analysis_musical_encounters.ipynb). Ensure that your Jupyter Notebook instance points to the **/data_analysis** directory to avoid path issues, or just modify the code to consider your full path. You possibly need to install additional Python packages for the notebook to run (e.g. you might need [`moviepy`](https://pypi.org/project/moviepy/))

## Going Further:

Check the main documentation of [this repository (README.md)](https://github.com/pedro-lucas-bravo/human_swarm_examples) for different examples in Python and other programming languages. Alternatively, you can explore additional features of the **HS-ims** app through its [OSC API](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main?tab=readme-ov-file#3-hs-ims-app-osc-api-documentation). If you experience any issue or want to provide a comment just contact me at the [Discord channel](https://discord.com/channels/1380190323711414304/1380480825778503801) of SysMus25.

**The theoretical material of the workshop will be shared after we finish the session at the conference.**