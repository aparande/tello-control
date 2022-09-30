"""Module for a PID Controller for Tello Yaw"""
from __future__ import annotations
from typing import Callable, Optional

import logging

from collections.abc import Iterable
import time

from tello_control import Tello, TelloController, TelemetryPacket, TelloEvent

LOGGER = logging.getLogger("controller")


class YawPidController(TelloController):
  """A Pid controller for Tello Yaw"""
  def __init__(
      self, tello: Tello, k_p: float, k_d: float, k_i: float,
      reference: Callable[[float], tuple[float, float]]
  ):
    self.k_p = k_p
    self.k_d = k_d
    self.k_i = k_i
    self.reference = reference

    self.last_telem: Optional[TelemetryPacket] = None
    self.last_error = None
    self.integrated_error = 0.0
    super().__init__(tello)

  def start(self):
    self.integrated_error = 0.0
    super().start()

  def compute_reference(
      self, now_time: float, telemetry: list[TelemetryPacket]
  ) -> Iterable[float]:
    return self.reference(now_time - self.start_time)

  def step(
      self, telemetry: list[TelemetryPacket]
  ) -> tuple[float, float, float, float]:
    curr_time = time.time()
    ref_yaw, _ = self.compute_reference(curr_time, telemetry)

    if len(telemetry) == 0 and self.last_telem is not None:
      # If a packet was dropped, use the last known yaw
      self.tello.log_event(TelloEvent.DROPPED_PACKET, level=logging.WARNING)
      curr_yaw = self.last_telem.yaw
    elif len(telemetry) == 0:
      # If we aren't receiving any telemetry, don't do anything
      return 0, 0, 0, 0
    else:
      curr_yaw = telemetry[-1].yaw

    error = ref_yaw - curr_yaw

    d_err = 0.0
    if self.last_error is not None:
      d_err = (error - self.last_error) * self._control_frequency

    self.integrated_error += error / self._control_frequency

    ua = self.k_p * error + self.k_d * d_err + self.k_i * self.integrated_error

    self.last_error = error

    if len(telemetry) >= 1:
      # Update the last known telemetry
      self.last_telem = telemetry[-1]

    # Only send a yaw control
    return 0, 0, 0, ua
