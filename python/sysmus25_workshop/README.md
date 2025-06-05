# SysMus25 Workshop - Human-Swarm Interactive Music Systems: Implementation and data analysis using Python

In this repository, you will find the materials necessary for the workshop taking place at SysMus25. The aim of this workshop is to provide fundamental concepts regarding *human-swarm interactive music systems*, as well as considerations for their design, implementation, and data analysis. The set of examples provided here serves as an explanatory artifact to support this goal. You can further develop the code and construct your own system based on it, or create a new system considering the information shared in the workshop.

As the emphasis shifts more towards the concepts and abstractions behind this topic illustrated in the code example, it is acceptable for you to attend without setting up this environment. However, it would be ideal for you to experience how these types of systems work on your machine. In that regard, please follow this document to ensure that you can run the examples BEFORE the workshop. If you encounter any issues, you can contact me at my email address: <pedroplu@ifi.uio.no>

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

* Download the application for visualization and interaction in a 3D environment according to your operative system:

    * [HS-ims Windows](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/win_ims.zip) (Open the *Human Swarm IMS.exe* file to check that the app is working)

    * [HS-ims Mac](https://github.com/pedro-lucas-bravo/human_swarm_examples/releases/download/v1.0.0/mac_ims.zip) (Open the .app file)
    
    > MacOS users may encounter issues when attempting to open this app. In this case, open a terminal and run the command `xattr -rc [PATH_TO_APP]` then try to open the app again.

* For the system part: Install [Python](https://www.python.org/downloads/) >= 3.11.5 with the following packages:
    * [numpy](https://pypi.org/project/numpy/)
    * [python-osc](https://pypi.org/project/python-osc/)

* For the data analysis part: Install an environment that allows you to use [Jupyter Notebooks](https://jupyter.org/) (Based also on Python)

* **Optional:** You can use the IDE of your preference, but in this workshop I will illustrate and run the examples through [Visual Studio Code](https://code.visualstudio.com/).


## Running the Examples

1. Download this repository in your machine: https://github.com/pedro-lucas-bravo/human_swarm_examples. For this workshop, you will only need the content found in the folder **<PATH_WHERE_YOU_DOWNLOAD>\human_swarm_examples\python\sysmus25_workshop**

2. Open the **HS-ims** app as mentioned in the previous section.

3. Inside the **sysmus25_workshop** you will find the folder **HS_systems** with two examples:
    * [template](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main/python/sysmus25_workshop/HS_systems/template): Contains some basic blocks to implement a human-swarm music system.
    * [example_1](https://github.com/pedro-lucas-bravo/human_swarm_examples/tree/main/python/sysmus25_workshop/HS_systems/example_1): It is based on the **template** and contains additional elements. This is the one that will be explained in the workshop.

In any of these folders you will find the script **main.py**. Run first the one in the **template**. A way to do this is opening a terminal, navigate to the folder **template** and exeute the corresponding command. The following is an example using PowerShell in Windows:


```lang-sh
<PATH_WHERE_YOU_DOWNLOAD>\human_swarm_examples\python\sysmus25_workshop\HS_systems\template> python .\main.py
```

You will be prompt the following:

```lang-sh
Serving on ('127.0.0.1', 6010)
Enter a command: 
```

Reduce considerably the sound volume of your machine before running since it can too noise. Then, write "**run**" to start the system. E.g:

```lang-sh
Serving on ('127.0.0.1', 6010)
Enter a command: run
```

You must be able to see in the **HS-ims** app something similar to the image below, and hear constantly pitch changing sounds.

![template](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/docs/imgs/template_img.png)

You can stop everything by writing "**exit**" in the console, which will terminate the Python script.

You can do the same for **example_1** by navigating in the corresponding folder and executing the **main.py** script. In that case, you must observe in the app something like the next image, together with reverberated punctual musical sounds.

![example_1](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/docs/imgs/example_1_img.png)

Again, you can stop by writing "**exit**" in the console. You can alternatively kill the terminal and close the **HS-ims** app.

At this point you are ready for the workshop, where more details will be provided. However, you can try some features that you will find in every example as described below.

### Example: HS_systems/template

[IN CONSTRUCTION]

### Example: HS_systems/example_1

[IN CONSTRUCTION]

## Data Analysis

[IN CONSTRUCTION]

Check the notebook [data_analysis_example_1.ipynb](https://github.com/pedro-lucas-bravo/human_swarm_examples/blob/main/python/sysmus25_workshop/data_analysis/data_analysis_example_1.ipynb)

Data from: https://doi.org/10.5281/zenodo.15602365
