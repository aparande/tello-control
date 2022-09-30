Examples
======================

To run any of these examples, install the ``tello_control`` package and run the `main.py` function.

Yaw PID Controller
------------------
``examples/yaw_pid`` contains an example of an experiment which controls the
Tello's yaw using a PID controller with user-specified gains. It will test the
controller on 3 different reference waves, each with 3 settings. The reference
waves are a sine, a sawtooth, and a square.  The settings are 0.1 Hz with 100
degree amplitude, 0.5 Hz with 50 degree amplitude, and 1 Hz with 20 degree
amplitude. Optionally, one can compare the results to an Open Loop Controller.

Usage: ::

	usage: main.py [-h] [--run-open-loop] [-kp KP] [-kd KD] [-ki KI] name

	Run an experiment for the PID medium article

	positional arguments:
		name             Experiment name

	optional arguments:
		-h, --help       show this help message and exit
		--run-open-loop  Whether to compare to an Open Loop Controller
		-kp KP           Proportional Gain
		-kd KD           Derivative Gain
		-ki KI           Integrator Gain

