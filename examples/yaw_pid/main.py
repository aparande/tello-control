#!/usr/bin/python3
"""
An experiment which runs a PID Controller on the drone's yaw and optionally
compares it to an Open Loop Controller for several different test references.
"""
from __future__ import annotations
from typing import Callable, Optional, Union

import pathlib

import argparse
import os
import logging
import time

import numpy as np

from pid_controller import YawPidController
from open_loop_controller import YawOpenLoopController
from tello_control import Experiment, TelloCommand

LOGGER = logging.getLogger("experiment")
RESULTS_BASE_PATH = pathlib.Path("results/pid-article")


def make_sin_reference(
    amplitude_deg: float, frequency_hz: float
) -> Callable[[float], tuple[float, float]]:
  """Create a sine function

  Args:
    amplitude_deg: Amplitude of the sine in degrees
    frequency_hz: Frequency of the sine in hertz
  Returns:
    A function which takes in a time and returns the wave value and its
    derivative at that time.
  """
  def sin_func(t: float) -> tuple[float, float]:
    sin = amplitude_deg * np.sin(2 * np.pi * frequency_hz * t)
    sin_vel = 2 * np.pi * frequency_hz * amplitude_deg * np.cos(
        2 * np.pi * frequency_hz * t
    )
    return sin, sin_vel

  return sin_func


def make_sawtooth_reference(
    amplitude_deg: float, frequency_hz: float
) -> Callable[[float], tuple[float, float]]:
  """Create a sawtooth wave function

  Args:
    amplitude_deg: Amplitude of the sawtooth in degrees
    frequency_hz: Frequency of the sawtooth in hertz
  Returns:
    A function which takes in a time and returns the wave value and its
    derivative at that time.
  """
  def sawtooth_func(t: float) -> tuple[float, float]:
    period_s = 1 / frequency_hz
    quarter_period_s = period_s / 4

    quarter_period_offset = t % quarter_period_s

    segment = (t // quarter_period_s) % 4
    direction = 1 if segment in (0, 3) else -1
    slope = amplitude_deg / quarter_period_s * direction

    if segment == 3:
      val = -amplitude_deg + slope * quarter_period_offset
    elif segment == 1:
      val = slope * quarter_period_offset + amplitude_deg
    else:
      val = slope * quarter_period_offset

    return val, slope

  return sawtooth_func


def make_square_reference(
    amplitude_deg: float, frequency_hz: float
) -> Callable[[float], tuple[float, float]]:
  """Create a square wave function

  Args:
    amplitude_deg: Amplitude of the square wave in degrees
    frequency_hz: Frequency of the square wave in hertz
  Returns:
    A function which takes in a time and returns the wave value and its
    derivative at that time.
  """
  def square_func(t: float) -> tuple[float, float]:
    period_s = 1 / frequency_hz
    half_period_s = period_s / 2

    mult = -2 * ((t // half_period_s) % 2) + 1
    return mult * amplitude_deg, 0

  return square_func


class PidYawControlExperiment(Experiment):
  """The main experiment which runs the PID Controller

  Args:
    output_path: Where to save the experiment results
    kp: The proportional gain
    kd: The derivative gain
    ki: The intgral gain
    run_open_loop: Whether to compare the PID to an open loop controller or not
  """
  def __init__(
      self,
      output_path: pathlib.Path,
      kp: float,
      kd: float,
      ki: float,
      run_open_loop: bool = False
  ):
    self.kp = kp
    self.kd = kd
    self.ki = ki
    self.run_open_loop = run_open_loop
    self.active_controller: Optional[Union[YawOpenLoopController,
                                            YawPidController]] = None

    super().__init__(output_path)

  def _hover(self, sec):
    start = time.time()
    while time.time() - start < sec:
      self.tello.send_command(TelloCommand.RC, 0, 0, 0, 0)
      time.sleep(0.1)

  def tearDown(self):
    if self.active_controller:
      self.active_controller.stop()
    super().tearDown()

  def main(self):
    ret, _ = self.tello.send_command(
        TelloCommand.TAKE_OFF, wait_for_success=True
    )
    if not ret:
      LOGGER.error(f"Takeoff failed. Tello battery is {self.tello.battery}%")
      return

    amplitudes = [100, 50, 20]
    freqs = [0.1, 0.5, 1]
    ref_funcs = [
        ("Sin", make_sin_reference), ("Sawtooth", make_sawtooth_reference),
        ("Square", make_square_reference)
    ]

    LOGGER.info("Hovering")
    self._hover(1)

    for name, ref_func in ref_funcs:
      for amp, freq in zip(amplitudes, freqs):
        LOGGER.info(
            f"Testing with {name} wave, Amplitude: {amp} degrees,\
            frequency: {freq} Hz"
        )
        reference = ref_func(amp, freq)
        if self.run_open_loop:
          LOGGER.info("Beginning Open Loop Control")
          self.active_controller = YawOpenLoopController(self.tello, reference)
          self.active_controller.start()

          time.sleep(20)

          self.active_controller.stop()

          LOGGER.info("Hovering")
          self._hover(1)

        LOGGER.info("Beginning Closed Loop Control")
        self.active_controller = YawPidController(
            self.tello, self.kp, self.kd, self.ki, reference
        )
        self.active_controller.start()

        time.sleep(20)

        self.active_controller.stop()

        LOGGER.info("Hovering")
        self._hover(1)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description="Run an experiment for the PID medium article"
  )
  parser.add_argument(
      "--run-open-loop",
      action="store_true",
      dest="run_open_loop",
      help="Whether to compare to an Open Loop Controller"
  )
  parser.add_argument("name", help="Experiment name")
  parser.add_argument("-kp", help="Proportional Gain", default=0, type=float)
  parser.add_argument("-kd", help="Derivative Gain", default=0, type=float)
  parser.add_argument("-ki", help="Integrator Gain", default=0, type=float)

  args = parser.parse_args()

  exp_path = RESULTS_BASE_PATH / args.name
  if not os.path.exists(exp_path):
    os.mkdir(exp_path)

  logging.basicConfig(
      format="%(asctime)s(%(name)s):%(levelname)s - %(message)s",
      level=logging.INFO,
      handlers=[
          logging.FileHandler(f"{exp_path}/experiment.log"),
          logging.StreamHandler()
      ]
  )

  experiment = PidYawControlExperiment(
      exp_path, args.kp, args.kd, args.ki, run_open_loop=args.run_open_loop
  )
  experiment.run()
