# DeepCool

## About
Open-source project to develop an ambient temperature controller for microscope enclosures. In particular, the goal is to address the dearth of off-the-shelf solutions for less-than-room-temperature cooling of microscope enclosures.  

This solution was inspired by and is used as part of the [Gravity Machine microscope](https://github.com/deepakkrishnamurthy/gravitymachine-research.git) for ensuring tempertaure stability and avoiding thermal gradients, as well as achieving temperature profiles found in ocean environments.

## Overview of design

The device used off-the-shelf peltier based heating/cooling system, as well as off-the-shelf tempartaure controllers interfaced via a Teensy microcontroller, that in turn communicates with a PC/Computer (PyQt based GUI for measuring and setting tempertature profiles). The device allows dynamic/programmatic setting of temperature profiles.  

## Selected Publications
1. Krishnamurthy, Deepak, Hongquan Li, François Benoit du Rey, Pierre Cambournac, Adam G. Larson, Ethan Li, and Manu Prakash. "Scale-free vertical tracking microscopy." Nature Methods (2020): 1-12. [Weblink](https://www.nature.com/articles/s41592-020-0924-7)
2. Krishnamurthy, Deepak, Hongquan Li, François Benoit du Rey, Pierre Cambournac, Adam Larson, and Manu Prakash. "Scale-free Vertical Tracking Microscopy: Towards Bridging Scales in Biological Oceanography." bioRxiv (2019): 610246. [Weblink](https://doi.org/10.1101/610246)
